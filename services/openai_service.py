import os
import time
import requests
from typing import Dict, Optional
from config import Config

class OpenAIService:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        
    def generate_blog_article(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Generate a comprehensive blog article from meeting transcript
        """
        if not self.api_key:
            return self._mock_generate_blog(transcript, meeting_details)
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create comprehensive prompt for blog generation
            prompt = f"""
            Create a comprehensive, professional blog article based on this meeting transcript. This should be a detailed, research-backed article suitable for business professionals and industry leaders.

            MEETING CONTEXT:
            - Title: {meeting_details.get('title', 'Business Meeting')}
            - Date: {meeting_details.get('date', 'Recent')}
            - Duration: {meeting_details.get('duration', 'Unknown')} minutes

            TRANSCRIPT CONTENT:
            {transcript}

            REQUIREMENTS FOR THE BLOG ARTICLE:

            1. **LENGTH & DEPTH**: Create a comprehensive article (1500-2500 words) with detailed analysis and insights.

            2. **STRUCTURE**:
               - Compelling headline that captures the main theme
               - Executive summary (2-3 paragraphs)
               - Detailed introduction with context and background
               - 4-6 main sections with subheadings
               - Industry analysis and trends
               - Data-driven insights and recommendations
               - Actionable takeaways and next steps
               - Conclusion with strategic implications

            3. **CONTENT REQUIREMENTS**:
               - Include relevant industry statistics and research
               - Reference current market trends and best practices
               - Add expert insights and case studies where applicable
               - Provide actionable recommendations
               - Include data visualization suggestions
               - Address potential challenges and solutions
               - Discuss long-term strategic implications

            4. **RESEARCH ELEMENTS**:
               - Incorporate relevant industry data and statistics
               - Reference current business trends and market analysis
               - Include expert opinions and industry benchmarks
               - Add competitive analysis if applicable
               - Reference relevant business frameworks and methodologies

            5. **TONE & STYLE**:
               - Professional and authoritative
               - Data-driven and analytical
               - Engaging but sophisticated
               - Suitable for C-level executives and business leaders
               - Include industry-specific terminology and insights

            6. **SECTIONS TO INCLUDE**:
               - Executive Summary
               - Introduction and Context
               - Key Discussion Points (detailed analysis)
               - Industry Trends and Market Analysis
               - Strategic Implications
               - Implementation Roadmap
               - Risk Assessment and Mitigation
               - Success Metrics and KPIs
               - Conclusion and Next Steps

            Make this a high-quality, comprehensive business article that provides real value to readers and positions the organization as a thought leader in the industry.
            """
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a senior business analyst and thought leader who creates comprehensive, research-backed business articles. You have deep expertise in strategic planning, market analysis, and business transformation. Your articles are detailed, data-driven, and provide actionable insights for business leaders."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000,
                "temperature": 0.7
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            blog_content = result['choices'][0]['message']['content']
            
            return {
                'success': True,
                'blog_content': blog_content,
                'word_count': len(blog_content.split()),
                'generated_at': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_poster_prompt(self, transcript: str, meeting_details: Dict) -> str:
        """
        Generate a prompt for poster image generation with meeting details
        """
        # Extract key information for poster
        title = meeting_details.get('title', 'Business Meeting')
        date = meeting_details.get('date', 'Recent')
        duration = meeting_details.get('duration', 0)
        
        # Extract meeting details from transcript
        meeting_info = self._extract_meeting_info(transcript)
        
        # Create a simplified visual prompt for DALL-E
        prompt = f"""
        Create a clean, professional meeting poster with ONLY these essential elements:

        MEETING INFORMATION:
        - MEETING HOLDER: {meeting_info.get('holder', 'Business Team')}
        - AGENDA: {meeting_info.get('agenda', 'Business discussion and planning')}
        - DATE: {date}
        - TIME: {duration} minutes duration

        DESIGN REQUIREMENTS:
        - Clean, minimalist business flyer design (flat design, no 3D effects), juat one poster in one page 
        - Professional corporate colors: blues, grays, whites
        - Large, clear typography for the meeting holder name
        - Simple layout with just the 4 essential elements
        - Clean background with subtle professional styling
        - NO extra text, NO icons, NO complex layouts
        - Focus only on: Holder, Agenda, Date, Time
        - NO room background, NO wall placement - just a flat flyer

        The poster should be simple and clean, showing only the meeting holder, agenda, date, and time in a professional business format.
        """
        
        return prompt.strip()
    
    def generate_poster_image(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Generate a poster image using DALL-E
        """
        if not self.api_key:
            return self._mock_generate_poster(transcript, meeting_details)
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = self.generate_poster_prompt(transcript, meeting_details)
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "standard",
                "style": "natural"
            }
            
            response = requests.post(f"{self.base_url}/images/generations", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            return {
                'success': True,
                'image_url': image_url,
                'prompt': prompt,
                'generated_at': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _mock_generate_blog(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Mock blog generation for testing without API key
        """
        print(f"Mock: Generating comprehensive blog article for meeting: {meeting_details.get('title', 'Business Meeting')}")
        time.sleep(2)  # Simulate processing time
        
        title = meeting_details.get('title', 'Business Meeting')
        
        blog_content = f"""
# Strategic Transformation: Key Insights from {title} and Industry Implications

## Executive Summary

Our recent {title} marked a pivotal moment in our organization's strategic evolution, bringing together key stakeholders to address critical business challenges and opportunities. This comprehensive analysis delves into the meeting's outcomes, industry context, and strategic implications for future growth and competitive positioning.

The discussion revealed significant insights into market dynamics, operational efficiency, and strategic positioning that will shape our organization's trajectory over the next 12-18 months. This article provides a detailed examination of these findings and their broader industry implications.

## Introduction and Context

In today's rapidly evolving business landscape, organizations must continuously adapt their strategies to maintain competitive advantage and drive sustainable growth. The {title} was convened to address these critical challenges and opportunities, bringing together cross-functional leadership to assess current performance and chart a course for future success.

The meeting's agenda encompassed strategic planning, performance optimization, resource allocation, and market positioning—topics that are increasingly relevant in today's dynamic business environment. This analysis provides a comprehensive overview of the discussions, insights, and strategic implications.

## Key Discussion Points and Strategic Analysis

### 1. Strategic Planning and Market Positioning

The team engaged in comprehensive strategic planning discussions, focusing on long-term goals and market positioning. Key insights emerged regarding competitive dynamics and market opportunities that will inform our strategic direction.

**Industry Context**: According to recent market research, organizations that engage in regular strategic planning outperform their peers by 23% in revenue growth and 18% in profitability. Our strategic planning session aligned with these best practices, incorporating market analysis, competitive intelligence, and scenario planning.

**Strategic Implications**: The discussion highlighted the importance of agile strategic planning in today's volatile market conditions. Organizations must balance long-term vision with short-term adaptability to maintain competitive advantage.

### 2. Performance Optimization and Operational Excellence

Performance review discussions revealed critical insights into operational efficiency and improvement opportunities. The team analyzed current performance metrics against industry benchmarks and identified key areas for optimization.

**Data-Driven Insights**: Performance analysis indicated that operational efficiency improvements could yield 15-20% cost savings while maintaining or improving service quality. This aligns with industry trends where leading organizations focus on continuous improvement and operational excellence.

**Implementation Strategy**: The team developed a comprehensive roadmap for performance optimization, including process improvements, technology investments, and capability development initiatives.

### 3. Resource Allocation and Investment Strategy

Critical decisions were made regarding resource allocation and investment priorities. The discussion focused on optimizing resource utilization while ensuring strategic alignment and risk management.

**Investment Priorities**: The team identified key investment areas including technology modernization, talent development, and market expansion initiatives. These priorities align with industry trends where successful organizations invest heavily in digital transformation and human capital development.

**Risk Management**: Comprehensive risk assessment was conducted for each investment area, with mitigation strategies developed to address potential challenges and uncertainties.

## Industry Trends and Market Analysis

### Current Market Dynamics

The business landscape is experiencing significant transformation driven by technological advancement, changing customer expectations, and evolving competitive dynamics. Organizations must adapt to these changes to maintain relevance and competitive advantage.

**Technology Trends**: Digital transformation continues to accelerate, with organizations investing heavily in automation, artificial intelligence, and data analytics. These investments are critical for maintaining competitive advantage and operational efficiency.

**Customer Expectations**: Customer expectations are evolving rapidly, with increasing demand for personalized experiences, seamless digital interactions, and sustainable business practices.

### Competitive Landscape Analysis

The competitive landscape is becoming increasingly dynamic, with new entrants and established players adapting their strategies to capture market opportunities. Organizations must continuously monitor and respond to competitive developments.

**Competitive Intelligence**: Regular monitoring of competitor activities, market positioning, and strategic initiatives is essential for maintaining competitive advantage and identifying new opportunities.

## Strategic Implications and Implementation Roadmap

### Short-term Strategic Initiatives (0-6 months)

1. **Performance Optimization**: Implement identified operational improvements to achieve 15-20% efficiency gains
2. **Technology Investment**: Begin technology modernization initiatives to enhance digital capabilities
3. **Talent Development**: Launch comprehensive talent development programs to build critical capabilities

### Medium-term Strategic Initiatives (6-18 months)

1. **Market Expansion**: Execute market expansion strategies to capture new opportunities
2. **Digital Transformation**: Complete digital transformation initiatives to enhance competitive positioning
3. **Strategic Partnerships**: Develop strategic partnerships to enhance capabilities and market reach

### Long-term Strategic Vision (18+ months)

1. **Market Leadership**: Achieve market leadership position in key segments
2. **Innovation Leadership**: Establish innovation leadership through continuous investment in R&D and new technologies
3. **Sustainable Growth**: Implement sustainable growth strategies that balance financial performance with social and environmental responsibility

## Risk Assessment and Mitigation Strategies

### Identified Risks

1. **Market Volatility**: Economic uncertainty and market volatility could impact strategic initiatives
2. **Technology Disruption**: Rapid technological change could render current strategies obsolete
3. **Competitive Pressure**: Intensifying competition could impact market position and profitability

### Mitigation Strategies

1. **Agile Strategy Execution**: Implement agile methodologies to enable rapid adaptation to changing market conditions
2. **Continuous Innovation**: Establish continuous innovation processes to stay ahead of technological disruption
3. **Competitive Intelligence**: Develop comprehensive competitive intelligence capabilities to monitor and respond to competitive developments

## Success Metrics and Key Performance Indicators

### Financial Metrics

- Revenue growth targets: 15-20% annual growth
- Profitability improvement: 10-15% margin enhancement
- Return on investment: 25%+ ROI for strategic initiatives

### Operational Metrics

- Operational efficiency: 20% improvement in key processes
- Customer satisfaction: 90%+ customer satisfaction scores
- Employee engagement: 85%+ employee engagement scores

### Strategic Metrics

- Market share growth: 5-10% market share increase
- Innovation pipeline: 3-5 new product/service launches annually
- Digital transformation: 80%+ digital adoption across key processes

## Conclusion and Next Steps

The {title} provided critical insights and strategic direction that will guide our organization's growth and competitive positioning over the next 18 months. The comprehensive analysis and strategic planning conducted during this meeting will serve as the foundation for our continued success and market leadership.

**Immediate Next Steps**:
1. Finalize strategic implementation plans and resource allocation
2. Establish governance structures for strategic initiative execution
3. Develop detailed project plans and timelines for key initiatives
4. Implement monitoring and reporting mechanisms for strategic progress

**Long-term Strategic Focus**:
1. Maintain focus on strategic priorities while remaining agile to market changes
2. Continue investment in technology and talent development
3. Build sustainable competitive advantages through innovation and operational excellence
4. Establish thought leadership position in the industry

This strategic transformation journey will require commitment, collaboration, and continuous adaptation, but the potential rewards in terms of market position, financial performance, and organizational capability are significant. By executing these strategic initiatives effectively, we will position our organization for sustained success and market leadership in the years ahead.

*Generated from meeting transcript analysis using advanced AI technology and industry research methodologies.*
        """
        
        return {
            'success': True,
            'blog_content': blog_content,
            'word_count': len(blog_content.split()),
            'generated_at': time.time()
        }
    
    def _mock_generate_poster(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Mock poster generation for testing without API key
        """
        print(f"Mock: Generating poster for meeting: {meeting_details.get('title', 'Business Meeting')}")
        time.sleep(2)  # Simulate processing time
        
        # Create a mock poster file
        poster_filename = f"poster_{int(time.time())}.jpg"
        poster_path = os.path.join('static', 'posters', poster_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(poster_path), exist_ok=True)
        
        # Create a dummy poster file
        with open(poster_path, 'w') as f:
            f.write(f"Mock poster for {meeting_details.get('title', 'Business Meeting')}")
        
        return {
            'success': True,
            'image_url': f'/static/posters/{poster_filename}',
            'prompt': self.generate_poster_prompt(transcript, meeting_details),
            'generated_at': time.time()
        } 

    def _extract_meeting_info(self, transcript: str) -> Dict:
        """
        Extract meeting information from transcript for poster generation
        """
        info = {
            'holder': 'Business Team',
            'agenda': 'Business discussion and planning',
            'topics': 'Strategic planning and team updates',
            'participants': 'Team members and stakeholders',
            'location': 'Conference Room / Virtual Meeting',
            'timing': 'To be scheduled'
        }
        
        # Extract meeting holder and topics from transcript
        if transcript:
            # Look for meeting holder (person leading the meeting)
            transcript_lower = transcript.lower()
            
            # Common patterns for meeting holder identification
            holder_patterns = [
                'i am', 'my name is', 'this is', 'hello everyone, i\'m',
                'good morning, i\'m', 'good afternoon, i\'m', 'hi, i\'m',
                'welcome everyone, i\'m', 'thank you for joining, i\'m'
            ]
            
            for pattern in holder_patterns:
                if pattern in transcript_lower:
                    # Extract the name after the pattern
                    start_idx = transcript_lower.find(pattern) + len(pattern)
                    end_idx = transcript_lower.find(' ', start_idx + 1)
                    if end_idx > start_idx:
                        holder_name = transcript[start_idx:end_idx].strip()
                        if len(holder_name) > 2:  # Valid name length
                            info['holder'] = holder_name.title()
                            break
            
            # Look for common meeting phrases for agenda
            if 'quarterly' in transcript_lower:
                info['agenda'] = 'Quarterly review and planning'
            elif 'strategy' in transcript_lower:
                info['agenda'] = 'Strategic planning session'
            elif 'performance' in transcript_lower:
                info['agenda'] = 'Performance review and discussion'
            elif 'project' in transcript_lower:
                info['agenda'] = 'Project planning and updates'
            elif 'budget' in transcript_lower:
                info['agenda'] = 'Budget review and planning'
            elif 'team' in transcript_lower:
                info['agenda'] = 'Team meeting and updates'
            
            # Extract agenda items
            agenda_items = []
            lines = transcript.split('.')
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['discuss', 'review', 'plan', 'update', 'present']):
                    agenda_items.append(line.capitalize())
            
            if agenda_items:
                info['agenda'] = '; '.join(agenda_items[:2])  # Take first 2 items
        
        return info 