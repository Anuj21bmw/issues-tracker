# backend/app/ai/document_processor.py
import logging
import os
import tempfile
from typing import Dict, List, Optional, Any
from PIL import Image
import pytesseract
from pathlib import Path
from app.ai.base import AIBaseService

logger = logging.getLogger(__name__)

class DocumentProcessor(AIBaseService):
    """AI-powered document analysis and information extraction"""
    
    def __init__(self):
        super().__init__()
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        self.supported_text_formats = {'.txt', '.md', '.log'}
        
        # Error pattern recognition
        self.error_patterns = {
            'stack_trace': [
                r'Traceback \(most recent call last\)',
                r'Exception in thread',
                r'at \w+\.\w+\([^)]+\)',
                r'\w+Error: .+',
                r'Caused by: .+'
            ],
            'http_errors': [
                r'HTTP/\d\.\d \d{3}',
                r'Status: \d{3}',
                r'Error \d{3}:'
            ],
            'database_errors': [
                r'SQL Error',
                r'Connection refused',
                r'Timeout occurred',
                r'Deadlock detected'
            ],
            'javascript_errors': [
                r'Uncaught \w+Error:',
                r'at Object\.<anonymous>',
                r'TypeError: Cannot read'
            ]
        }
        
        # Technology detection patterns
        self.tech_patterns = {
            'languages': {
                'python': ['python', 'django', 'flask', 'fastapi', 'pytest'],
                'javascript': ['javascript', 'node.js', 'react', 'vue', 'angular'],
                'java': ['java', 'spring', 'hibernate', 'maven', 'gradle'],
                'csharp': ['c#', '.net', 'asp.net', 'entity framework'],
                'php': ['php', 'laravel', 'symfony', 'composer'],
                'ruby': ['ruby', 'rails', 'gem', 'bundler']
            },
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'spring', 'express'],
            'services': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'nginx']
        }
    
    async def process_document(self, file_path: str, file_name: str) -> Dict:
        """Process uploaded document and extract insights"""
        try:
            file_ext = Path(file_name).suffix.lower()
            
            if file_ext in self.supported_image_formats:
                return await self._process_image(file_path, file_name)
            elif file_ext in self.supported_text_formats:
                return await self._process_text_file(file_path, file_name)
            else:
                return {
                    'file_type': 'unsupported',
                    'message': f'File type {file_ext} not supported for analysis',
                    'extracted_text': None,
                    'insights': []
                }
        
        except Exception as e:
            logger.error(f"Document processing failed for {file_name}: {e}")
            return {
                'file_type': 'error',
                'message': f'Failed to process document: {str(e)}',
                'extracted_text': None,
                'insights': []
            }
    
    async def _process_image(self, file_path: str, file_name: str) -> Dict:
        """Process image file using OCR"""
        try:
            # Open and preprocess image
            with Image.open(file_path) as image:
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Extract text using OCR
                extracted_text = pytesseract.image_to_string(image)
                
                if not extracted_text.strip():
                    return {
                        'file_type': 'image',
                        'message': 'No text could be extracted from the image',
                        'extracted_text': '',
                        'insights': []
                    }
                
                # Analyze extracted text
                analysis = await self._analyze_text_content(extracted_text)
                
                return {
                    'file_type': 'image',
                    'message': 'Successfully extracted text from image',
                    'extracted_text': extracted_text,
                    'text_length': len(extracted_text),
                    'confidence': self._estimate_ocr_confidence(extracted_text),
                    **analysis
                }
        
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                'file_type': 'image',
                'message': f'Failed to process image: {str(e)}',
                'extracted_text': None,
                'insights': []
            }
    
    async def _process_text_file(self, file_path: str, file_name: str) -> Dict:
        """Process text-based files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return {
                    'file_type': 'text',
                    'message': 'File appears to be empty',
                    'extracted_text': '',
                    'insights': []
                }
            
            # Analyze content
            analysis = await self._analyze_text_content(content)
            
            return {
                'file_type': 'text',
                'message': 'Successfully analyzed text file',
                'extracted_text': content[:2000] + ('...' if len(content) > 2000 else ''),  # Truncate for display
                'full_text_length': len(content),
                **analysis
            }
        
        except Exception as e:
            logger.error(f"Text file processing failed: {e}")
            return {
                'file_type': 'text',
                'message': f'Failed to process text file: {str(e)}',
                'extracted_text': None,
                'insights': []
            }
    
    async def _analyze_text_content(self, text: str) -> Dict:
        """Analyze text content for errors, technologies, and insights"""
        insights = []
        suggested_tags = []
        error_info = []
        
        # Detect errors and stack traces
        error_analysis = self._detect_errors(text)
        if error_analysis['errors_found']:
            insights.extend(error_analysis['insights'])
            suggested_tags.extend(error_analysis['suggested_tags'])
            error_info = error_analysis['error_details']
        
        # Detect technologies
        tech_analysis = self._detect_technologies(text)
        if tech_analysis['technologies']:
            insights.append(f"Technologies detected: {', '.join(tech_analysis['technologies'])}")
            suggested_tags.extend(tech_analysis['technologies'])
        
        # Extract key information
        key_info = self._extract_key_information(text)
        if key_info:
            insights.extend(key_info)
        
        # Generate AI insights if available
        ai_insights = await self._generate_ai_insights(text, error_info)
        if ai_insights:
            insights.extend(ai_insights)
        
        return {
            'insights': insights,
            'suggested_tags': list(set(suggested_tags))[:10],  # Unique tags, max 10
            'error_analysis': error_analysis,
            'technology_analysis': tech_analysis,
            'severity_indicators': self._assess_severity_indicators(text)
        }
    
    def _detect_errors(self, text: str) -> Dict:
        """Detect and analyze errors in text"""
        import re
        
        errors_found = []
        insights = []
        suggested_tags = []
        error_details = []
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    errors_found.append(error_type)
                    error_details.extend(matches)
                    
                    # Add specific insights based on error type
                    if error_type == 'stack_trace':
                        insights.append("🐛 Stack trace detected - this appears to be a runtime error")
                        suggested_tags.extend(['bug', 'error', 'crash'])
                    elif error_type == 'http_errors':
                        insights.append("🌐 HTTP error detected - likely API or network issue")
                        suggested_tags.extend(['api', 'network', 'http'])
                    elif error_type == 'database_errors':
                        insights.append("🗃️ Database error detected - check connection and queries")
                        suggested_tags.extend(['database', 'db', 'connection'])
                    elif error_type == 'javascript_errors':
                        insights.append("⚡ JavaScript error detected - frontend issue")
                        suggested_tags.extend(['frontend', 'javascript', 'ui'])
        
        return {
            'errors_found': len(errors_found) > 0,
            'error_types': list(set(errors_found)),
            'error_details': error_details[:5],  # Limit to first 5 errors
            'insights': insights,
            'suggested_tags': list(set(suggested_tags))
        }
    
    def _detect_technologies(self, text: str) -> Dict:
        """Detect technologies mentioned in the text"""
        detected_technologies = []
        text_lower = text.lower()
        
        # Check for programming languages
        for lang, keywords in self.tech_patterns['languages'].items():
            if any(keyword in text_lower for keyword in keywords):
                detected_technologies.append(lang)
        
        # Check for databases
        for db in self.tech_patterns['databases']:
            if db in text_lower:
                detected_technologies.append(db)
        
        # Check for frameworks
        for framework in self.tech_patterns['frameworks']:
            if framework in text_lower:
                detected_technologies.append(framework)
        
        # Check for services
        for service in self.tech_patterns['services']:
            if service in text_lower:
                detected_technologies.append(service)
        
        return {
            'technologies': list(set(detected_technologies)),
            'technology_count': len(set(detected_technologies))
        }
    
    def _extract_key_information(self, text: str) -> List[str]:
        """Extract key information and patterns"""
        insights = []
        text_lower = text.lower()
        
        # Check for URLs
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if urls:
            insights.append(f"🔗 {len(urls)} URL(s) found - may contain relevant endpoints")
        
        # Check for IP addresses
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
        if ips:
            insights.append(f"🌐 {len(ips)} IP address(es) found")
        
        # Check for file paths
        file_paths = re.findall(r'[/\\][\w\-_/\\\.]+\.\w+', text)
        if file_paths:
            insights.append(f"📁 {len(file_paths)} file path(s) identified")
        
        # Check for timestamps
        timestamps = re.findall(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}', text)
        if timestamps:
            insights.append(f"⏰ {len(timestamps)} timestamp(s) found")
        
        # Check for environment indicators
        env_keywords = ['production', 'staging', 'development', 'localhost', 'prod', 'dev']
        found_envs = [env for env in env_keywords if env in text_lower]
        if found_envs:
            insights.append(f"🏗️ Environment context: {', '.join(found_envs)}")
        
        return insights
    
    def _assess_severity_indicators(self, text: str) -> Dict:
        """Assess severity indicators in the text"""
        text_lower = text.lower()
        
        critical_indicators = ['critical', 'urgent', 'emergency', 'down', 'outage', 'crash']
        high_indicators = ['error', 'exception', 'fail', 'broken', 'bug']
        medium_indicators = ['warning', 'issue', 'problem', 'slow']
        
        critical_count = sum(1 for word in critical_indicators if word in text_lower)
        high_count = sum(1 for word in high_indicators if word in text_lower)
        medium_count = sum(1 for word in medium_indicators if word in text_lower)
        
        # Determine suggested severity
        if critical_count > 0:
            suggested_severity = 'CRITICAL'
        elif high_count > 1:
            suggested_severity = 'HIGH'
        elif high_count > 0 or medium_count > 1:
            suggested_severity = 'MEDIUM'
        else:
            suggested_severity = 'LOW'
        
        return {
            'suggested_severity': suggested_severity,
            'critical_indicators': critical_count,
            'high_indicators': high_count,
            'medium_indicators': medium_count,
            'severity_confidence': min(0.9, (critical_count + high_count + medium_count) * 0.2 + 0.3)
        }
    
    async def _generate_ai_insights(self, text: str, error_details: List[str]) -> List[str]:
        """Generate AI-powered insights about the document content"""
        try:
            if not text.strip():
                return []
            
            # Prepare text for AI analysis (limit length)
            analysis_text = text[:1500] + ('...' if len(text) > 1500 else '')
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a technical analyst. Analyze the provided text/error log and provide 2-3 concise, actionable insights. Focus on identifying the root cause, impact, and recommended actions."
                },
                {
                    "role": "user",
                    "content": f"""Analyze this technical content:

{analysis_text}

Provide 2-3 key insights about:
1. What the main issue appears to be
2. Potential root causes
3. Recommended next steps

Keep each insight to one sentence."""
                }
            ]
            
            ai_response = await self.call_openai_chat(messages, max_tokens=200)
            
            if ai_response and ai_response.strip():
                # Split AI response into individual insights
                insights = [insight.strip() for insight in ai_response.split('\n') if insight.strip()]
                return [f"🤖 {insight}" for insight in insights[:3]]  # Limit to 3 insights
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
        
        return []
    
    def _estimate_ocr_confidence(self, text: str) -> float:
        """Estimate OCR confidence based on text characteristics"""
        if not text.strip():
            return 0.0
        
        confidence = 0.7  # Base confidence
        
        # Check for common OCR issues
        total_chars = len(text)
        if total_chars == 0:
            return 0.0
        
        # Count suspicious characters that might indicate poor OCR
        suspicious_chars = text.count('|') + text.count('~') + text.count('{') + text.count('}')
        confidence -= min(0.3, suspicious_chars / total_chars * 2)
        
        # Check for reasonable word patterns
        words = text.split()
        if len(words) > 5:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if 2 <= avg_word_length <= 12:  # Reasonable word length
                confidence += 0.1
        
        # Check for complete sentences
        sentences = text.count('.') + text.count('!') + text.count('?')
        if sentences > 0:
            confidence += 0.1
        
        return max(0.1, min(0.95, confidence))
    
    async def analyze_log_file(self, file_path: str) -> Dict:
        """Specialized analysis for log files"""
        try:
            insights = []
            log_patterns = {
                'errors': r'\[?ERROR\]?|FATAL|CRITICAL',
                'warnings': r'\[?WARN\]?|\[?WARNING\]?',
                'info': r'\[?INFO\]?|\[?INFORMATION\]?',
                'debug': r'\[?DEBUG\]?|\[?TRACE\]?'
            }
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            log_stats = {}
            for level, pattern in log_patterns.items():
                import re
                matches = re.findall(pattern, content, re.IGNORECASE)
                log_stats[level] = len(matches)
            
            # Generate insights based on log analysis
            if log_stats.get('errors', 0) > 0:
                insights.append(f"🔥 {log_stats['errors']} error entries found in log")
            if log_stats.get('warnings', 0) > 10:
                insights.append(f"⚠️ High number of warnings: {log_stats['warnings']}")
            
            # Find most recent entries
            lines = content.split('\n')
            recent_errors = []
            for line in lines[-50:]:  # Check last 50 lines
                if any(pattern in line.upper() for pattern in ['ERROR', 'FATAL', 'CRITICAL']):
                    recent_errors.append(line.strip())
            
            return {
                'log_statistics': log_stats,
                'insights': insights,
                'recent_errors': recent_errors[:5],  # Last 5 errors
                'total_lines': len(lines),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Log file analysis failed: {e}")
            return {'error': f'Failed to analyze log file: {str(e)}'}
    
    def extract_code_snippets(self, text: str) -> List[Dict]:
        """Extract code snippets from text"""
        import re
        
        snippets = []
        
        # Look for code blocks (markdown style)
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', text, re.DOTALL)
        for lang, code in code_blocks:
            snippets.append({
                'type': 'code_block',
                'language': lang or 'unknown',
                'code': code.strip(),
                'line_count': len(code.strip().split('\n'))
            })
        
        # Look for inline code
        inline_code = re.findall(r'`([^`]+)`', text)
        for code in inline_code:
            if len(code) > 10:  # Only significant code snippets
                snippets.append({
                    'type': 'inline_code',
                    'language': 'unknown',
                    'code': code.strip(),
                    'line_count': 1
                })
        
        # Look for stack trace patterns
        stack_traces = re.findall(r'(.*Error.*(?:\n\s+at .+)+)', text, re.MULTILINE)
        for trace in stack_traces:
            snippets.append({
                'type': 'stack_trace',
                'language': 'stacktrace',
                'code': trace.strip(),
                'line_count': len(trace.strip().split('\n'))
            })
        
        return snippets[:10]  