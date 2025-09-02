"""
Comprehensive ATS Analysis Service
- Advanced formatting checks
- Graphics and table detection
- Content structure analysis
- ATS-friendly recommendations
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from ..utils.text_utils import has_sections, detect_contact_info

logger = logging.getLogger(__name__)

class ATSService:
    def __init__(self):
        # ATS-unfriendly patterns
        self.problematic_patterns = {
            'graphics_indicators': [
                r'image|img|figure|chart|graph|diagram|logo',
                r'\.png|\.jpg|\.jpeg|\.gif|\.svg|\.pdf',
                r'graphic|visual|illustration'
            ],
            'table_indicators': [
                r'\|\s*\w+\s*\|',  # Markdown table format
                r'\t\w+\t',        # Tab-separated content
                r'┌|┐|┘|└|├|┤|┬|┴|┼',  # Box drawing characters
            ],
            'formatting_issues': [
                r'[^\x00-\x7F]',    # Non-ASCII characters
                r'#{2,}',           # Multiple hash symbols
                r'={3,}',           # Multiple equals
                r'-{3,}',           # Multiple dashes as dividers
                r'_{3,}',           # Multiple underscores
            ],
            'complex_layouts': [
                r'\s{4,}\w+\s{4,}', # Multiple spaces (potential columns)
                r'\n\s*\n\s*\n',    # Multiple line breaks
            ]
        }
        
        # Contact information patterns
        self.contact_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'linkedin': r'linkedin\.com/in/[A-Za-z0-9-]+',
            'github': r'github\.com/[A-Za-z0-9-]+',
            'website': r'(https?://)?(www\.)?[A-Za-z0-9-]+\.[A-Za-z]{2,}'
        }
    
    def analyze_ats_compatibility(self, text: str, file_format: str = 'pdf') -> Dict[str, Any]:
        """Comprehensive ATS compatibility analysis"""
        analysis = {
            'overall_score': 0,
            'compatibility_level': '',
            'issues': [],
            'recommendations': [],
            'detailed_analysis': {}
        }
        
        # File format analysis
        format_analysis = self._analyze_file_format(file_format)
        analysis['detailed_analysis']['file_format'] = format_analysis
        
        # Structure analysis
        structure_analysis = self._analyze_structure(text)
        analysis['detailed_analysis']['structure'] = structure_analysis
        
        # Content formatting analysis
        formatting_analysis = self._analyze_formatting(text)
        analysis['detailed_analysis']['formatting'] = formatting_analysis
        
        # Graphics and tables analysis
        graphics_analysis = self._analyze_graphics_tables(text)
        analysis['detailed_analysis']['graphics_tables'] = graphics_analysis
        
        # Contact information analysis
        contact_analysis = self._analyze_contact_info(text)
        analysis['detailed_analysis']['contact_info'] = contact_analysis
        
        # Calculate overall score
        analysis['overall_score'] = self._calculate_ats_score(analysis['detailed_analysis'])
        analysis['compatibility_level'] = self._get_compatibility_level(analysis['overall_score'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_ats_recommendations(analysis['detailed_analysis'])
        
        # Collect all issues
        analysis['issues'] = self._collect_all_issues(analysis['detailed_analysis'])
        
        return analysis
    
    def _analyze_file_format(self, file_format: str) -> Dict[str, Any]:
        """Analyze file format compatibility"""
        format_scores = {
            'pdf': {'score': 90, 'recommendation': 'Excellent choice - widely supported'},
            'docx': {'score': 85, 'recommendation': 'Good choice - well supported'},
            'doc': {'score': 70, 'recommendation': 'Acceptable but consider newer formats'},
            'txt': {'score': 95, 'recommendation': 'Perfect for ATS but may lack formatting'},
            'rtf': {'score': 75, 'recommendation': 'Acceptable but less common'},
            'html': {'score': 60, 'recommendation': 'May have parsing issues'},
            'unknown': {'score': 50, 'recommendation': 'Unknown format - use PDF or DOCX'}
        }
        
        format_info = format_scores.get(file_format.lower(), format_scores['unknown'])
        
        return {
            'format': file_format,
            'score': format_info['score'],
            'recommendation': format_info['recommendation'],
            'is_ats_friendly': format_info['score'] >= 70
        }
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure for ATS compatibility"""
        lines = text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        analysis = {
            'total_lines': len(lines),
            'content_lines': len(non_empty_lines),
            'avg_line_length': sum(len(line) for line in non_empty_lines) / max(len(non_empty_lines), 1),
            'has_clear_sections': has_sections(text),
            'issues': [],
            'score': 0
        }
        
        # Check for structure issues
        if analysis['avg_line_length'] > 200:
            analysis['issues'].append('Lines are too long - may cause parsing issues')
        
        if len(non_empty_lines) < 20:
            analysis['issues'].append('Document appears too short')
        
        if not analysis['has_clear_sections']:
            analysis['issues'].append('Document lacks clear section structure')
        
        # Calculate score
        score = 50  # Base score
        if analysis['has_clear_sections']:
            score += 30
        if analysis['avg_line_length'] <= 150:
            score += 20
        if len(analysis['issues']) == 0:
            score += 20
        
        analysis['score'] = min(score, 100)
        
        return analysis
    
    def _analyze_formatting(self, text: str) -> Dict[str, Any]:
        """Analyze text formatting for ATS issues"""
        analysis = {
            'issues': [],
            'warnings': [],
            'score': 100,
            'character_analysis': {},
            'spacing_analysis': {}
        }
        
        # Check for non-ASCII characters
        non_ascii_chars = re.findall(r'[^\x00-\x7F]', text)
        if non_ascii_chars:
            unique_chars = set(non_ascii_chars)
            analysis['issues'].append(f'Contains {len(unique_chars)} types of non-ASCII characters')
            analysis['character_analysis']['non_ascii_count'] = len(non_ascii_chars)
            analysis['character_analysis']['unique_non_ascii'] = list(unique_chars)[:10]  # Sample
            analysis['score'] -= 15
        
        # Check for problematic formatting patterns
        for category, patterns in self.problematic_patterns.items():
            if category == 'graphics_indicators':
                continue  # Handled separately
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    analysis['warnings'].append(f'Found {category}: {len(matches)} instances')
                    analysis['score'] -= 5
        
        # Check spacing patterns
        excessive_spaces = re.findall(r' {3,}', text)
        if excessive_spaces:
            analysis['spacing_analysis']['excessive_spaces'] = len(excessive_spaces)
            analysis['warnings'].append('Contains excessive spacing that may confuse ATS')
            analysis['score'] -= 10
        
        # Check for tabs
        tab_count = text.count('\t')
        if tab_count > 0:
            analysis['spacing_analysis']['tab_count'] = tab_count
            analysis['warnings'].append('Contains tab characters - use spaces instead')
            analysis['score'] -= 5
        
        analysis['score'] = max(analysis['score'], 0)
        
        return analysis
    
    def _analyze_graphics_tables(self, text: str) -> Dict[str, Any]:
        """Analyze presence of graphics and tables"""
        analysis = {
            'graphics_detected': False,
            'tables_detected': False,
            'graphics_indicators': [],
            'table_indicators': [],
            'score': 100,
            'recommendations': []
        }
        
        # Check for graphics indicators
        for pattern in self.problematic_patterns['graphics_indicators']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                analysis['graphics_detected'] = True
                analysis['graphics_indicators'].extend(matches[:5])  # Sample
        
        # Check for table indicators
        for pattern in self.problematic_patterns['table_indicators']:
            if re.search(pattern, text):
                analysis['tables_detected'] = True
                analysis['table_indicators'].append(pattern)
        
        # Score deductions
        if analysis['graphics_detected']:
            analysis['score'] -= 30
            analysis['recommendations'].append('Remove graphics/images - use text descriptions instead')
        
        if analysis['tables_detected']:
            analysis['score'] -= 20
            analysis['recommendations'].append('Convert tables to simple text format with clear labels')
        
        return analysis
    
    def _analyze_contact_info(self, text: str) -> Dict[str, Any]:
        """Analyze contact information completeness and format"""
        analysis = {
            'found_contacts': {},
            'missing_contacts': [],
            'score': 0,
            'recommendations': []
        }
        
        # Check for each contact type
        for contact_type, pattern in self.contact_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                analysis['found_contacts'][contact_type] = matches[0]  # Take first match
            else:
                analysis['missing_contacts'].append(contact_type)
        
        # Score based on found contacts
        contact_count = len(analysis['found_contacts'])
        if contact_count >= 3:
            analysis['score'] = 100
        elif contact_count == 2:
            analysis['score'] = 80
        elif contact_count == 1:
            analysis['score'] = 60
        else:
            analysis['score'] = 30
        
        # Generate recommendations
        if 'email' not in analysis['found_contacts']:
            analysis['recommendations'].append('Add a professional email address')
        if 'phone' not in analysis['found_contacts']:
            analysis['recommendations'].append('Include a phone number')
        if 'linkedin' not in analysis['found_contacts'] and 'github' not in analysis['found_contacts']:
            analysis['recommendations'].append('Consider adding LinkedIn or GitHub profile')
        
        return analysis
    
    def _calculate_ats_score(self, detailed_analysis: Dict[str, Any]) -> int:
        """Calculate overall ATS compatibility score"""
        weights = {
            'file_format': 0.15,
            'structure': 0.25,
            'formatting': 0.20,
            'graphics_tables': 0.20,
            'contact_info': 0.20
        }
        
        total_score = 0
        for component, weight in weights.items():
            if component in detailed_analysis:
                component_score = detailed_analysis[component].get('score', 0)
                total_score += component_score * weight
        
        return int(total_score)
    
    def _get_compatibility_level(self, score: int) -> str:
        """Get compatibility level description"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Poor"
        else:
            return "Very Poor"
    
    def _generate_ats_recommendations(self, detailed_analysis: Dict[str, Any]) -> List[str]:
        """Generate comprehensive ATS recommendations"""
        recommendations = []
        
        # Collect recommendations from all components
        for component, analysis in detailed_analysis.items():
            if 'recommendations' in analysis:
                recommendations.extend(analysis['recommendations'])
            if 'recommendation' in analysis:  # Single recommendation
                recommendations.append(analysis['recommendation'])
        
        # Add general recommendations based on overall analysis
        if detailed_analysis.get('graphics_tables', {}).get('score', 100) < 80:
            recommendations.append('Simplify document layout for better ATS parsing')
        
        if detailed_analysis.get('formatting', {}).get('score', 100) < 70:
            recommendations.append('Use standard fonts and avoid complex formatting')
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _collect_all_issues(self, detailed_analysis: Dict[str, Any]) -> List[str]:
        """Collect all issues from detailed analysis"""
        all_issues = []
        
        for component, analysis in detailed_analysis.items():
            if 'issues' in analysis:
                all_issues.extend(analysis['issues'])
            if 'warnings' in analysis:
                all_issues.extend(analysis['warnings'])
        
        return all_issues

# Global instance for backward compatibility
_ats_service = ATSService()

def ats_heuristics(resume_text: str) -> tuple[dict, float]:
    """Backward compatibility function for basic ATS checks"""
    text = resume_text or ""
    
    # Use enhanced analysis but return simple format for compatibility
    full_analysis = _ats_service.analyze_ats_compatibility(text)
    
    checks = {
        "has_sections": has_sections(text),
        "has_contact_info": detect_contact_info(text),
        "no_photos_or_graphics": not full_analysis['detailed_analysis']['graphics_tables']['graphics_detected'],
        "reasonable_length": 300 <= len(text) <= 9000,
        "bullet_usage": bool(re.search(r"(^|\n)\s*[•\-\*]", text)),
        "no_tables_detected": not full_analysis['detailed_analysis']['graphics_tables']['tables_detected'],
        "simple_headings": True,
        "no_excessive_columns": True,
        "no_header_footer_text": True,
    }
    
    truthy = sum(1 for v in checks.values() if v)
    total = len(checks)
    score = round((truthy / total) * 100.0, 1)
    
    return checks, score

def analyze_ats_compatibility(text: str, file_format: str = 'pdf') -> Dict[str, Any]:
    """Enhanced ATS compatibility analysis"""
    return _ats_service.analyze_ats_compatibility(text, file_format)