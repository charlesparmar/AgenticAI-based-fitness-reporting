"""
Document Chunking Utilities for RAG Pipeline
Handles smart chunking of fitness data for vectorization
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class DocumentChunker:
    """Handles smart chunking of fitness data documents"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def create_fitness_chunks(self, fitness_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create document chunks from fitness data
        
        Args:
            fitness_data: List of fitness measurement records
            
        Returns:
            List of document chunks with metadata
        """
        chunks = []
        
        try:
            # Sort data by date for chronological chunking
            sorted_data = sorted(fitness_data, key=lambda x: x.get('date', ''))
            
            # Create individual measurement chunks
            for record in sorted_data:
                measurement_chunks = self._create_measurement_chunks(record)
                chunks.extend(measurement_chunks)
            
            # Create trend analysis chunks
            trend_chunks = self._create_trend_chunks(sorted_data)
            chunks.extend(trend_chunks)
            
            # Create summary chunks
            summary_chunks = self._create_summary_chunks(sorted_data)
            chunks.extend(summary_chunks)
            
            print(f"✅ Created {len(chunks)} document chunks from {len(fitness_data)} records")
            return chunks
            
        except Exception as e:
            print(f"❌ Error creating fitness chunks: {e}")
            return []
    
    def _create_measurement_chunks(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create chunks for individual measurement records"""
        chunks = []
        
        try:
            # Extract basic info
            date = record.get('date', '')
            week_number = record.get('week_number', '')
            
            # Create measurement summary
            measurements = {
                'weight': record.get('weight'),
                'fat_percent': record.get('fat_percent'),
                'bmi': record.get('bmi'),
                'fat_weight': record.get('fat_weight'),
                'lean_weight': record.get('lean_weight'),
                'neck': record.get('neck'),
                'shoulders': record.get('shoulders'),
                'biceps': record.get('biceps'),
                'forearms': record.get('forearms'),
                'chest': record.get('chest'),
                'above_navel': record.get('above_navel'),
                'navel': record.get('navel'),
                'waist': record.get('waist'),
                'hips': record.get('hips'),
                'thighs': record.get('thighs'),
                'calves': record.get('calves')
            }
            
            # Filter out None values
            valid_measurements = {k: v for k, v in measurements.items() if v is not None}
            
            # Create measurement text
            measurement_text = f"Week {week_number} measurements on {date}:\n"
            for measurement, value in valid_measurements.items():
                measurement_text += f"- {measurement.replace('_', ' ').title()}: {value}\n"
            
            # Create chunk with flattened metadata for ChromaDB
            chunk = {
                'content': measurement_text,
                'metadata': {
                    'type': 'measurement',
                    'date': str(date),
                    'week_number': str(week_number),
                    'chunk_id': f"measurement_{date}_{week_number}",
                    'weight': str(valid_measurements.get('weight', '')),
                    'fat_percent': str(valid_measurements.get('fat_percent', '')),
                    'bmi': str(valid_measurements.get('bmi', '')),
                    'waist': str(valid_measurements.get('waist', '')),
                    'chest': str(valid_measurements.get('chest', '')),
                    'hips': str(valid_measurements.get('hips', '')),
                    'units': 'weight_kg_body_inches_bmi_standard_fat_percent'
                }
            }
            
            chunks.append(chunk)
            
            # Create individual measurement chunks if there are many measurements
            if len(valid_measurements) > 8:
                # Split into body composition and body measurements
                body_comp = {k: v for k, v in valid_measurements.items() 
                           if k in ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight']}
                body_measurements = {k: v for k, v in valid_measurements.items() 
                                   if k not in ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight']}
                
                if body_comp:
                    comp_text = f"Week {week_number} body composition on {date}:\n"
                    for measurement, value in body_comp.items():
                        comp_text += f"- {measurement.replace('_', ' ').title()}: {value}\n"
                    
                    chunks.append({
                        'content': comp_text,
                        'metadata': {
                            'type': 'body_composition',
                            'date': str(date),
                            'week_number': str(week_number),
                            'chunk_id': f"composition_{date}_{week_number}",
                            'weight': str(body_comp.get('weight', '')),
                            'fat_percent': str(body_comp.get('fat_percent', '')),
                            'bmi': str(body_comp.get('bmi', '')),
                            'fat_weight': str(body_comp.get('fat_weight', '')),
                            'lean_weight': str(body_comp.get('lean_weight', '')),
                            'units': 'weight_kg_body_inches_bmi_standard_fat_percent'
                        }
                    })
                
                if body_measurements:
                    measure_text = f"Week {week_number} body measurements on {date}:\n"
                    for measurement, value in body_measurements.items():
                        measure_text += f"- {measurement.replace('_', ' ').title()}: {value}\n"
                    
                    chunks.append({
                        'content': measure_text,
                        'metadata': {
                            'type': 'body_measurements',
                            'date': str(date),
                            'week_number': str(week_number),
                            'chunk_id': f"measurements_{date}_{week_number}",
                            'neck': str(body_measurements.get('neck', '')),
                            'shoulders': str(body_measurements.get('shoulders', '')),
                            'biceps': str(body_measurements.get('biceps', '')),
                            'forearms': str(body_measurements.get('forearms', '')),
                            'chest': str(body_measurements.get('chest', '')),
                            'waist': str(body_measurements.get('waist', '')),
                            'hips': str(body_measurements.get('hips', '')),
                            'units': 'weight_kg_body_inches_bmi_standard_fat_percent'
                        }
                    })
            
        except Exception as e:
            print(f"❌ Error creating measurement chunks: {e}")
        
        return chunks
    
    def _create_trend_chunks(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create chunks for trend analysis"""
        chunks = []
        
        try:
            if len(data) < 2:
                return chunks
            
            # Create weekly trend chunks
            for i in range(1, len(data)):
                current = data[i]
                previous = data[i-1]
                
                trend_text = f"Trend analysis from week {previous.get('week_number', '')} to week {current.get('week_number', '')}:\n"
                
                # Calculate changes
                changes = {}
                for key in ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight']:
                    if current.get(key) is not None and previous.get(key) is not None:
                        change = current[key] - previous[key]
                        changes[key] = change
                
                if changes:
                    for key, change in changes.items():
                        direction = "increased" if change > 0 else "decreased" if change < 0 else "unchanged"
                        trend_text += f"- {key.replace('_', ' ').title()}: {direction} by {abs(change):.2f}\n"
                    
                    chunks.append({
                        'content': trend_text,
                        'metadata': {
                            'type': 'trend',
                            'date_from': str(previous.get('date', '')),
                            'date_to': str(current.get('date', '')),
                            'week_from': str(previous.get('week_number', '')),
                            'week_to': str(current.get('week_number', '')),
                            'chunk_id': f"trend_{previous.get('date', '')}_{current.get('date', '')}",
                            'weight_change': str(changes.get('weight', '')),
                            'fat_change': str(changes.get('fat_percent', '')),
                            'bmi_change': str(changes.get('bmi', ''))
                        }
                    })
            
            # Create monthly trend chunks (if we have enough data)
            if len(data) >= 4:
                monthly_chunks = self._create_monthly_trends(data)
                chunks.extend(monthly_chunks)
            
        except Exception as e:
            print(f"❌ Error creating trend chunks: {e}")
        
        return chunks
    
    def _create_monthly_trends(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create monthly trend analysis chunks"""
        chunks = []
        
        try:
            # Group by month
            monthly_data = {}
            for record in data:
                date = record.get('date', '')
                if date:
                    try:
                        month_key = date[:7]  # YYYY-MM format
                        if month_key not in monthly_data:
                            monthly_data[month_key] = []
                        monthly_data[month_key].append(record)
                    except:
                        continue
            
            # Create monthly summaries
            for month, records in monthly_data.items():
                if len(records) >= 2:
                    # Calculate monthly averages
                    avg_measurements = {}
                    for key in ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight']:
                        values = [r.get(key) for r in records if r.get(key) is not None]
                        if values:
                            avg_measurements[key] = sum(values) / len(values)
                    
                    if avg_measurements:
                        month_text = f"Monthly summary for {month}:\n"
                        month_text += f"Number of measurements: {len(records)}\n"
                        for key, value in avg_measurements.items():
                            month_text += f"Average {key.replace('_', ' ')}: {value:.2f}\n"
                        
                        chunks.append({
                            'content': month_text,
                            'metadata': {
                                'type': 'monthly_summary',
                                'month': str(month),
                                'record_count': str(len(records)),
                                'chunk_id': f"monthly_{month}",
                                'avg_weight': str(avg_measurements.get('weight', '')),
                                'avg_fat_percent': str(avg_measurements.get('fat_percent', '')),
                                'avg_bmi': str(avg_measurements.get('bmi', ''))
                            }
                        })
            
        except Exception as e:
            print(f"❌ Error creating monthly trends: {e}")
        
        return chunks
    
    def _create_summary_chunks(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create summary chunks for the entire dataset"""
        chunks = []
        
        try:
            if not data:
                return chunks
            
            # Overall summary
            total_records = len(data)
            date_range = f"{data[0].get('date', '')} to {data[-1].get('date', '')}"
            
            # Calculate overall statistics
            stats = {}
            for key in ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight']:
                values = [r.get(key) for r in data if r.get(key) is not None]
                if values:
                    stats[key] = {
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'count': len(values)
                    }
            
            summary_text = f"Fitness data summary:\n"
            summary_text += f"Total records: {total_records}\n"
            summary_text += f"Date range: {date_range}\n"
            
            for key, stat in stats.items():
                summary_text += f"\n{key.replace('_', ' ').title()}:\n"
                summary_text += f"- Range: {stat['min']:.2f} to {stat['max']:.2f}\n"
                summary_text += f"- Average: {stat['avg']:.2f}\n"
                summary_text += f"- Measurements: {stat['count']}\n"
            
            chunks.append({
                'content': summary_text,
                'metadata': {
                    'type': 'overall_summary',
                    'total_records': str(total_records),
                    'date_range': str(date_range),
                    'chunk_id': 'overall_summary',
                    'min_weight': str(stats.get('weight', {}).get('min', '')),
                    'max_weight': str(stats.get('weight', {}).get('max', '')),
                    'avg_weight': str(stats.get('weight', {}).get('avg', '')),
                    'min_fat_percent': str(stats.get('fat_percent', {}).get('min', '')),
                    'max_fat_percent': str(stats.get('fat_percent', {}).get('max', '')),
                    'avg_fat_percent': str(stats.get('fat_percent', {}).get('avg', ''))
                }
            })
            
        except Exception as e:
            print(f"❌ Error creating summary chunks: {e}")
        
        return chunks
    
    def split_text_chunks(self, text: str) -> List[str]:
        """
        Split long text into smaller chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        try:
            if len(text) <= self.chunk_size:
                return [text]
            
            # Simple character-based splitting
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                
                # Try to break at sentence boundary
                if end < len(text):
                    # Look for sentence endings
                    for i in range(end, max(start, end - 100), -1):
                        if text[i] in '.!?':
                            end = i + 1
                            break
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                start = end - self.chunk_overlap
                if start >= len(text):
                    break
            
        except Exception as e:
            print(f"❌ Error splitting text chunks: {e}")
            # Fallback to simple splitting
            chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        
        return chunks 