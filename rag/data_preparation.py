"""
Data Preparation Module for RAG Pipeline
Extracts and preprocesses fitness data from SQLite Cloud
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlitecloud
from .utils.chunking import DocumentChunker
from .utils.embeddings import EmbeddingManager


class DataPreparation:
    """Handles data extraction and preprocessing for RAG pipeline"""
    
    def __init__(self, embedding_provider: str = "sentence-transformers", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize data preparation
        
        Args:
            embedding_provider: Embedding provider to use
            embedding_model: Embedding model name
        """
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        self.connection_string = None
        self.chunker = DocumentChunker()
        self.embedding_manager = EmbeddingManager(embedding_provider, embedding_model)
        
        if self.sqlite_api_key:
            # Use the same connection format as your existing agents
            self.connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={self.sqlite_api_key}"
    
    def extract_fitness_data(self) -> List[Dict[str, Any]]:
        """
        Extract fitness data from SQLite Cloud database
        
        Returns:
            List of fitness measurement records
        """
        try:
            if not self.sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return []
            
            if not self.connection_string:
                print("❌ Connection string not available")
                return []
            
            print("🔄 Connecting to SQLite Cloud...")
            conn = sqlitecloud.connect(self.connection_string)
            
            # Query all fitness data from fitness_measurements table
            query = """
                SELECT date, weight, fat_percent, bmi, fat_weight, lean_weight, 
                       neck, shoulders, biceps, forearms, chest, above_navel, 
                       navel, waist, hips, thighs, calves, week_number
                FROM fitness_measurements 
                ORDER BY week_number DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            print(f"✅ Extracted {len(df)} records from fitness_measurements table")
            
            # Convert DataFrame to list of dictionaries
            records = []
            for _, row in df.iterrows():
                record = {
                    'date': row['date'],
                    'weight': row['weight'],
                    'fat_percent': row['fat_percent'],
                    'bmi': row['bmi'],
                    'fat_weight': row['fat_weight'],
                    'lean_weight': row['lean_weight'],
                    'neck': row['neck'],
                    'shoulders': row['shoulders'],
                    'biceps': row['biceps'],
                    'forearms': row['forearms'],
                    'chest': row['chest'],
                    'above_navel': row['above_navel'],
                    'navel': row['navel'],
                    'waist': row['waist'],
                    'hips': row['hips'],
                    'thighs': row['thighs'],
                    'calves': row['calves']
                }
                
                # Use week_number from database if available, otherwise calculate
                if 'week_number' in row and row['week_number'] is not None:
                    record['week_number'] = row['week_number']
                else:
                    # Standardize date and calculate week number
                    standardized_date = self._standardize_date(row['date'])
                    if standardized_date:
                        record['date'] = standardized_date
                        record['week_number'] = self._calculate_week_number(standardized_date)
                    else:
                        record['week_number'] = "Unknown"
                records.append(record)
            
            return records
            
        except Exception as e:
            print(f"❌ Error extracting fitness data: {e}")
            return []
    
    def _standardize_date(self, date_str: str) -> Optional[str]:
        """
        Standardize date string to dd mm yyyy format
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Standardized date string in dd mm yyyy format or None if invalid
        """
        try:
            if not date_str:
                return None
            
            # Try different date formats
            date_formats = [
                "%Y-%m-%d",      # 2024-01-15
                "%d-%m-%Y",      # 15-01-2024
                "%m-%d-%Y",      # 01-15-2024
                "%Y/%m/%d",      # 2024/01/15
                "%d/%m/%Y",      # 15/01/2024
                "%m/%d/%Y",      # 01/15/2024
                "%d %m %Y",      # 15 01 2024
                "%Y %m %d",      # 2024 01 15
                "%d.%m.%Y",      # 15.01.2024
                "%Y.%m.%d",      # 2024.01.15
            ]
            
            date_obj = None
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    break
                except ValueError:
                    continue
            
            if not date_obj:
                print(f"❌ Unable to parse date: {date_str}")
                return None
            
            # Return in dd-mm-yyyy format
            return date_obj.strftime("%d-%m-%Y")
            
        except Exception as e:
            print(f"❌ Error standardizing date {date_str}: {e}")
            return None

    def _calculate_week_number(self, date_str: str) -> str:
        """
        Calculate week number from date string
        
        Args:
            date_str: Date string in dd mm yyyy format
            
        Returns:
            Week number string
        """
        try:
            if not date_str:
                return "Unknown"
            
            # Parse date in dd-mm-yyyy format
            try:
                date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            except ValueError:
                # Fallback to old format parsing if needed
                date_obj = None
                for fmt in ["%d %m %Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            if not date_obj:
                raise ValueError(f"Unable to parse date: {date_str}")
            
            # Calculate week number (simple approach)
            # You might want to use a more sophisticated week calculation
            week_num = date_obj.isocalendar()[1]
            year = date_obj.year
            
            return f"Week {week_num} ({year})"
            
        except Exception as e:
            print(f"❌ Error calculating week number for {date_str}: {e}")
            return "Unknown"
    
    def preprocess_data(self, fitness_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess fitness data for vectorization
        
        Args:
            fitness_data: Raw fitness data records
            
        Returns:
            Preprocessed fitness data
        """
        try:
            if not fitness_data:
                return []
            
            print("🔄 Preprocessing fitness data...")
            
            preprocessed_data = []
            
            for record in fitness_data:
                # Clean and validate data
                cleaned_record = self._clean_record(record)
                
                if cleaned_record:
                    preprocessed_data.append(cleaned_record)
            
            print(f"✅ Preprocessed {len(preprocessed_data)} records")
            return preprocessed_data
            
        except Exception as e:
            print(f"❌ Error preprocessing data: {e}")
            return []
    
    def _clean_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean and validate a single record
        
        Args:
            record: Raw record data
            
        Returns:
            Cleaned record or None if invalid
        """
        try:
            cleaned_record = {}
            
            # Validate required fields
            if not record.get('date'):
                return None
            
            # Standardize date to dd mm yyyy format
            standardized_date = self._standardize_date(record['date'])
            if not standardized_date:
                return None
            
            # Add standardized date
            cleaned_record['date'] = standardized_date
            
            # Copy and clean fields
            for key, value in record.items():
                if value is not None and key != 'date':  # Skip date as it's already handled
                    # Convert numeric values
                    if key in ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight',
                              'neck', 'shoulders', 'biceps', 'forearms', 'chest', 
                              'above_navel', 'navel', 'waist', 'hips', 'thighs', 'calves']:
                        try:
                            cleaned_record[key] = float(value)
                        except (ValueError, TypeError):
                            # Skip invalid numeric values
                            continue
                    else:
                        cleaned_record[key] = value
            
            # Ensure we have at least some measurements
            measurement_keys = ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight',
                              'neck', 'shoulders', 'biceps', 'forearms', 'chest', 
                              'above_navel', 'navel', 'waist', 'hips', 'thighs', 'calves']
            
            has_measurements = any(key in cleaned_record for key in measurement_keys)
            
            if not has_measurements:
                return None
            
            return cleaned_record
            
        except Exception as e:
            print(f"❌ Error cleaning record: {e}")
            return None
    
    def create_document_chunks(self, fitness_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create document chunks from fitness data
        
        Args:
            fitness_data: Preprocessed fitness data
            
        Returns:
            List of document chunks with metadata
        """
        try:
            print("🔄 Creating document chunks...")
            
            chunks = self.chunker.create_fitness_chunks(fitness_data)
            
            print(f"✅ Created {len(chunks)} document chunks")
            return chunks
            
        except Exception as e:
            print(f"❌ Error creating document chunks: {e}")
            return []
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks
        
        Args:
            chunks: List of document chunks
            
        Returns:
            List of chunks with embeddings
        """
        try:
            if not chunks:
                return []
            
            print("🔄 Generating embeddings...")
            
            # Extract content for embedding
            contents = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_manager.get_embeddings(contents)
            
            if not embeddings:
                print("❌ Failed to generate embeddings")
                return chunks
            
            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                if i < len(embeddings):
                    chunk['embedding'] = embeddings[i]
            
            print(f"✅ Generated embeddings for {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return chunks
    
    def prepare_vector_data(self) -> List[Dict[str, Any]]:
        """
        Complete data preparation pipeline
        
        Returns:
            List of chunks ready for vector storage
        """
        try:
            print("🚀 Starting data preparation pipeline...")
            
            # Step 1: Extract data
            fitness_data = self.extract_fitness_data()
            if not fitness_data:
                print("❌ No fitness data extracted")
                return []
            
            # Step 2: Preprocess data
            preprocessed_data = self.preprocess_data(fitness_data)
            if not preprocessed_data:
                print("❌ No data after preprocessing")
                return []
            
            # Step 3: Create chunks
            chunks = self.create_document_chunks(preprocessed_data)
            if not chunks:
                print("❌ No chunks created")
                return []
            
            # Step 4: Generate embeddings
            chunks_with_embeddings = self.generate_embeddings(chunks)
            
            print(f"✅ Data preparation complete: {len(chunks_with_embeddings)} chunks ready")
            return chunks_with_embeddings
            
        except Exception as e:
            print(f"❌ Error in data preparation pipeline: {e}")
            return []
    
    def get_data_statistics(self, fitness_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the fitness data
        
        Args:
            fitness_data: List of fitness records
            
        Returns:
            Dictionary with data statistics
        """
        try:
            if not fitness_data:
                return {"error": "No data available"}
            
            stats = {
                "total_records": len(fitness_data),
                "date_range": {
                    "start": min(record.get('date', '') for record in fitness_data if record.get('date')),
                    "end": max(record.get('date', '') for record in fitness_data if record.get('date'))
                },
                "measurements": {}
            }
            
            # Calculate statistics for each measurement type
            measurement_keys = ['weight', 'fat_percent', 'bmi', 'fat_weight', 'lean_weight',
                              'neck', 'shoulders', 'biceps', 'forearms', 'chest', 
                              'above_navel', 'navel', 'waist', 'hips', 'thighs', 'calves']
            
            for key in measurement_keys:
                values = [record.get(key) for record in fitness_data if record.get(key) is not None]
                if values:
                    stats["measurements"][key] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values)
                    }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error calculating data statistics: {e}")
            return {"error": str(e)} 