#!/usr/bin/env python3
"""
AST-Aware Code Chunker for Engram.

Unlike simple text chunking, this understands code structure:
- Extracts functions, classes, methods as complete units
- Preserves docstrings and signatures
- Adds rich metadata (name, type, parameters)
- Falls back to text chunking for unsupported languages

Supported languages:
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Go (.go) - basic support
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """A meaningful unit of code."""
    content: str
    chunk_type: str  # 'function', 'class', 'method', 'module', 'block'
    name: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    metadata: Dict

    def to_document(self):
        """Convert to LangChain Document format."""
        from langchain_core.documents import Document

        # Create a rich header for better search
        header_parts = [f"# {self.chunk_type.upper()}: {self.name}"]

        if self.metadata.get('class_name'):
            header_parts.append(f"# In class: {self.metadata['class_name']}")

        if self.metadata.get('signature'):
            header_parts.append(f"# Signature: {self.metadata['signature']}")

        if self.metadata.get('docstring'):
            header_parts.append(f"# Docstring: {self.metadata['docstring'][:200]}")

        header = "\n".join(header_parts)
        full_content = f"{header}\n\n{self.content}"

        return Document(
            page_content=full_content,
            metadata={
                "source_file": self.file_path,
                "source_type": "code_ast",
                "chunk_type": self.chunk_type,
                "name": self.name,
                "start_line": self.start_line,
                "end_line": self.end_line,
                "language": self.language,
                **self.metadata
            }
        )


class PythonChunker:
    """AST-based chunker for Python code."""

    def chunk(self, code: str, file_path: str) -> List[CodeChunk]:
        """Extract functions and classes from Python code."""
        chunks = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Fall back to text chunking if parse fails
            return []

        lines = code.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                chunk = self._extract_function(node, lines, file_path)
                if chunk:
                    chunks.append(chunk)

            elif isinstance(node, ast.ClassDef):
                chunk = self._extract_class(node, lines, file_path)
                if chunk:
                    chunks.append(chunk)

        # If no functions/classes found, return module-level chunk
        if not chunks and code.strip():
            chunks.append(CodeChunk(
                content=code,
                chunk_type='module',
                name=Path(file_path).stem,
                file_path=file_path,
                start_line=1,
                end_line=len(lines),
                language='python',
                metadata={}
            ))

        return chunks

    def _extract_function(self, node: ast.FunctionDef, lines: List[str], file_path: str) -> Optional[CodeChunk]:
        """Extract a function definition."""
        start_line = node.lineno
        end_line = node.end_lineno or start_line

        # Get the actual code
        content = '\n'.join(lines[start_line - 1:end_line])

        # Extract signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        signature = f"{node.name}({', '.join(args)})"

        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"

        # Extract docstring
        docstring = ast.get_docstring(node) or ""

        # Check if it's a method (inside a class)
        class_name = None
        for parent in ast.walk(ast.parse('\n'.join(lines))):
            if isinstance(parent, ast.ClassDef):
                for child in ast.iter_child_nodes(parent):
                    if child == node or (hasattr(child, 'lineno') and child.lineno == node.lineno):
                        class_name = parent.name
                        break

        return CodeChunk(
            content=content,
            chunk_type='method' if class_name else 'function',
            name=node.name,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            language='python',
            metadata={
                'signature': signature,
                'docstring': docstring,
                'class_name': class_name,
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'decorators': [ast.unparse(d) for d in node.decorator_list]
            }
        )

    def _extract_class(self, node: ast.ClassDef, lines: List[str], file_path: str) -> Optional[CodeChunk]:
        """Extract a class definition (header + docstring, not methods)."""
        start_line = node.lineno

        # Find where the class body starts (after docstring)
        body_start = start_line
        for child in node.body:
            if isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant):
                # This is likely the docstring
                body_start = child.end_lineno or body_start
            else:
                break

        # Get class header + docstring only (methods extracted separately)
        end_line = min(body_start + 5, node.end_lineno or start_line)  # Limit to header
        content = '\n'.join(lines[start_line - 1:end_line])

        # Extract base classes
        bases = [ast.unparse(base) for base in node.bases]

        # Extract docstring
        docstring = ast.get_docstring(node) or ""

        return CodeChunk(
            content=content,
            chunk_type='class',
            name=node.name,
            file_path=file_path,
            start_line=start_line,
            end_line=node.end_lineno or end_line,
            language='python',
            metadata={
                'bases': bases,
                'docstring': docstring,
                'decorators': [ast.unparse(d) for d in node.decorator_list],
                'method_count': sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            }
        )


class JavaScriptChunker:
    """Regex-based chunker for JavaScript/TypeScript."""

    # Patterns for JS/TS
    FUNCTION_PATTERN = re.compile(
        r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{',
        re.MULTILINE
    )

    ARROW_FUNCTION_PATTERN = re.compile(
        r'^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*\w+)?\s*=>\s*\{?',
        re.MULTILINE
    )

    CLASS_PATTERN = re.compile(
        r'^(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{',
        re.MULTILINE
    )

    METHOD_PATTERN = re.compile(
        r'^\s+(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{',
        re.MULTILINE
    )

    def chunk(self, code: str, file_path: str) -> List[CodeChunk]:
        """Extract functions and classes from JavaScript/TypeScript."""
        chunks = []
        lines = code.split('\n')

        # Find functions
        for match in self.FUNCTION_PATTERN.finditer(code):
            chunk = self._extract_block(match, code, lines, file_path, 'function')
            if chunk:
                chunks.append(chunk)

        # Find arrow functions
        for match in self.ARROW_FUNCTION_PATTERN.finditer(code):
            chunk = self._extract_block(match, code, lines, file_path, 'function')
            if chunk:
                chunks.append(chunk)

        # Find classes
        for match in self.CLASS_PATTERN.finditer(code):
            chunk = self._extract_block(match, code, lines, file_path, 'class')
            if chunk:
                chunks.append(chunk)

        # If nothing found, return whole file
        if not chunks and code.strip():
            chunks.append(CodeChunk(
                content=code[:2000],  # Limit size
                chunk_type='module',
                name=Path(file_path).stem,
                file_path=file_path,
                start_line=1,
                end_line=len(lines),
                language='javascript',
                metadata={}
            ))

        return chunks

    def _extract_block(self, match, code: str, lines: List[str], file_path: str, chunk_type: str) -> Optional[CodeChunk]:
        """Extract a code block by matching braces."""
        start_pos = match.start()
        name = match.group(1)

        # Find start line
        start_line = code[:start_pos].count('\n') + 1

        # Find matching closing brace
        brace_count = 0
        in_string = False
        string_char = None
        end_pos = match.end()

        for i, char in enumerate(code[match.start():], match.start()):
            if char in '"\'`' and (i == 0 or code[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break

        content = code[match.start():end_pos]
        end_line = start_line + content.count('\n')

        # Limit chunk size
        if len(content) > 3000:
            content = content[:3000] + "\n// ... (truncated)"

        # Detect language
        ext = Path(file_path).suffix.lower()
        language = 'typescript' if ext in ['.ts', '.tsx'] else 'javascript'

        return CodeChunk(
            content=content,
            chunk_type=chunk_type,
            name=name,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            language=language,
            metadata={
                'signature': match.group(0).strip()[:100]
            }
        )


class GoChunker:
    """Regex-based chunker for Go code."""

    FUNCTION_PATTERN = re.compile(
        r'^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\([^)]*\)\s*(?:\([^)]*\)|[\w\[\]]+)?\s*\{',
        re.MULTILINE
    )

    TYPE_PATTERN = re.compile(
        r'^type\s+(\w+)\s+(?:struct|interface)\s*\{',
        re.MULTILINE
    )

    def chunk(self, code: str, file_path: str) -> List[CodeChunk]:
        """Extract functions and types from Go code."""
        chunks = []
        lines = code.split('\n')

        # Find functions
        for match in self.FUNCTION_PATTERN.finditer(code):
            chunk = self._extract_block(match, code, lines, file_path, 'function')
            if chunk:
                chunks.append(chunk)

        # Find types
        for match in self.TYPE_PATTERN.finditer(code):
            chunk = self._extract_block(match, code, lines, file_path, 'type')
            if chunk:
                chunks.append(chunk)

        return chunks

    def _extract_block(self, match, code: str, lines: List[str], file_path: str, chunk_type: str) -> Optional[CodeChunk]:
        """Extract a Go code block."""
        start_pos = match.start()
        name = match.group(1)
        start_line = code[:start_pos].count('\n') + 1

        # Find matching brace
        brace_count = 0
        end_pos = match.end()

        for i, char in enumerate(code[match.start():], match.start()):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break

        content = code[match.start():end_pos]
        end_line = start_line + content.count('\n')

        return CodeChunk(
            content=content,
            chunk_type=chunk_type,
            name=name,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            language='go',
            metadata={
                'signature': match.group(0).strip()[:100]
            }
        )


class ASTChunker:
    """
    Main AST chunker that delegates to language-specific chunkers.

    Usage:
        chunker = ASTChunker()
        chunks = chunker.chunk_file(Path("example.py"))
        documents = [chunk.to_document() for chunk in chunks]
    """

    CHUNKERS = {
        '.py': PythonChunker(),
        '.js': JavaScriptChunker(),
        '.jsx': JavaScriptChunker(),
        '.ts': JavaScriptChunker(),
        '.tsx': JavaScriptChunker(),
        '.go': GoChunker(),
    }

    def chunk_file(self, file_path: Path) -> List[CodeChunk]:
        """Chunk a file using AST if supported, otherwise return empty list."""
        ext = file_path.suffix.lower()

        if ext not in self.CHUNKERS:
            return []

        try:
            code = file_path.read_text(encoding='utf-8')
        except:
            try:
                code = file_path.read_text(encoding='latin-1')
            except:
                return []

        chunker = self.CHUNKERS[ext]
        return chunker.chunk(code, str(file_path))

    def chunk_code(self, code: str, file_path: str, language: str = None) -> List[CodeChunk]:
        """Chunk code string directly."""
        if language:
            ext = f'.{language}'
        else:
            ext = Path(file_path).suffix.lower()

        if ext not in self.CHUNKERS:
            return []

        chunker = self.CHUNKERS[ext]
        return chunker.chunk(code, file_path)

    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(self.CHUNKERS.keys())


def chunk_code_files(files: List[Path]) -> Tuple[List, List[Path]]:
    """
    Chunk multiple code files using AST.

    Returns:
        Tuple of (documents, files_not_chunked)
        - documents: LangChain Documents from AST chunking
        - files_not_chunked: Files that couldn't be AST-chunked (use text chunking)
    """
    chunker = ASTChunker()
    documents = []
    not_chunked = []

    for file_path in files:
        chunks = chunker.chunk_file(file_path)

        if chunks:
            documents.extend([chunk.to_document() for chunk in chunks])
        else:
            not_chunked.append(file_path)

    return documents, not_chunked
