import os
import logging
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import bcrypt
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_ANON_KEY
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(url, key)
    
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase.table(Config.DATABASE_TABLE).select("*").eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by telegram ID {telegram_id}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase.table(Config.DATABASE_TABLE).select("*").eq('username', username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def create_user(self, telegram_id: int, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            hashed_password = self.hash_password(password)
            response = self.supabase.table(Config.DATABASE_TABLE).insert({
                'telegram_id': telegram_id,
                'username': username,
                'password_hash': hashed_password
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None
    
    def update_user_profile(self, telegram_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table(Config.DATABASE_TABLE).update(update_data).eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user profile for telegram_id {telegram_id}: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.get_user_by_username(username)
            if user and self.verify_password(password, user['password_hash']):
                return user
            return None
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def is_profile_complete(self, telegram_id: int) -> bool:
        user = self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        return all([
            user.get('tank_volume') is not None,
            user.get('soil_volume') is not None
        ])
    
    def create_feeding_log(self, telegram_id: int, greens: float, browns: float, moisture_percentage: float) -> Optional[Dict[str, Any]]:
        """
        Create a new feeding log entry
        
        Args:
            telegram_id: User's telegram ID
            greens: Amount of greens added (in grams)
            browns: Amount of browns added (in grams)  
            moisture_percentage: Moisture percentage achieved after feeding
            
        Returns:
            Created feeding log entry or None if failed
        """
        try:
            # Get the user to retrieve the username
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found for telegram_id {telegram_id}")
                return None
            
            response = self.supabase.table('feeding_logs').insert({
                'telegram_id': telegram_id,
                'username': user['username'],  # Add username to the feeding log
                'greens': greens,
                'browns': browns,
                'moisture_percentage': moisture_percentage
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating feeding log for telegram_id {telegram_id}: {e}")
            return None
    
    def get_user_feeding_logs(self, telegram_id: int, limit: int = 10) -> list:
        """
        Get recent feeding logs for a user
        
        Args:
            telegram_id: User's telegram ID
            limit: Number of recent logs to retrieve
            
        Returns:
            List of feeding log entries
        """
        try:
            response = self.supabase.table('feeding_logs').select("*").eq('telegram_id', telegram_id).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting feeding logs for telegram_id {telegram_id}: {e}")
            return []
    
    def get_user_total_food_waste(self, telegram_id: int) -> float:
        """
        Calculate total food waste (greens + browns) for a specific user from feeding logs
        
        Args:
            telegram_id: User's telegram ID
            
        Returns:
            Total food waste in kg
        """
        try:
            response = self.supabase.table('feeding_logs').select("greens, browns").eq('telegram_id', telegram_id).execute()
            if not response.data:
                return 0.0
            
            total_grams = sum(log.get('greens', 0) + log.get('browns', 0) for log in response.data)
            return round(total_grams / 1000, 2)  # Convert grams to kg
        except Exception as e:
            logger.error(f"Error calculating total food waste for telegram_id {telegram_id}: {e}")
            return 0.0
    
    def get_all_users_total_food_waste(self) -> float:
        """
        Calculate total food waste (greens + browns) for all NutriBot users from feeding logs
        
        Returns:
            Total food waste across all users in kg
        """
        try:
            response = self.supabase.table('feeding_logs').select("greens, browns").execute()
            if not response.data:
                return 0.0
            
            total_grams = sum(log.get('greens', 0) + log.get('browns', 0) for log in response.data)
            return round(total_grams / 1000, 2)  # Convert grams to kg
        except Exception as e:
            logger.error(f"Error calculating total food waste for all users: {e}")
            return 0.0
    
    def create_plant_moisture_log(self, telegram_id: int, plant_moisture: float) -> Optional[Dict[str, Any]]:
        """
        Create a new plant moisture log entry
        
        Args:
            telegram_id: User's telegram ID
            plant_moisture: Current plant moisture percentage
            
        Returns:
            Created plant moisture log entry or None if failed
        """
        try:
            # Get the user to retrieve the username
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found for telegram_id {telegram_id}")
                return None
            
            response = self.supabase.table('plant').insert({
                'telegram_id': telegram_id,
                'username': user['username'],
                'plant_moisture': plant_moisture
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating plant moisture log for telegram_id {telegram_id}: {e}")
            return None
    
    def get_user_plant_moisture_logs(self, telegram_id: int, limit: int = 10) -> list:
        """
        Get recent plant moisture logs for a user
        
        Args:
            telegram_id: User's telegram ID
            limit: Number of recent logs to retrieve
            
        Returns:
            List of plant moisture log entries
        """
        try:
            response = self.supabase.table('plant').select("*").eq('telegram_id', telegram_id).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting plant moisture logs for telegram_id {telegram_id}: {e}")
            return []

    def create_compost_status_with_predictions(self, telegram_id: int, ec: float, moisture: float, predictions: Dict) -> Optional[Dict[str, Any]]:
        """
        Create a new compost status entry with comprehensive ML predictions and analysis
        
        Args:
            telegram_id: User's telegram ID
            ec: EC value in mS/cm
            moisture: Moisture percentage
            predictions: Dictionary containing complete prediction results
            
        Returns:
            Created record or None if failed
        """
        try:
            # Get username for the record
            user = self.get_user_by_telegram_id(telegram_id)
            username = user.get('username', 'unknown') if user else 'unknown'
            
            # Prepare the base data for insertion
            insert_data = {
                'telegram_id': telegram_id,
                'username': username,
                'ec': ec,
                'moisture': moisture,
                'created_at': datetime.now().isoformat()
            }
            
            # Add comprehensive prediction data if available
            if predictions.get('success', False):
                # Basic prediction metadata
                insert_data.update({
                    'prediction_generated': True,
                    'prediction_success': True,
                    'forecast_date': datetime.now().isoformat()
                })
                
                # Key time-based predictions
                key_preds = predictions.get('key_predictions', {})
                insert_data.update({
                    'week_1_prediction': key_preds.get('week_1'),
                    'week_2_prediction': key_preds.get('week_2'),
                    'month_1_prediction': key_preds.get('month_1'),
                    'month_2_prediction': key_preds.get('month_2'),
                    'month_3_prediction': key_preds.get('month_3')
                })
                
                # 90-day statistics
                stats = predictions.get('statistics', {})
                insert_data.update({
                    'avg_ec_prediction': stats.get('average_ec'),
                    'max_ec_prediction': stats.get('max_ec'),
                    'min_ec_prediction': stats.get('min_ec')
                })
                
                # Store complete prediction arrays for dashboard charts
                if 'predictions' in predictions and 'dates' in predictions:
                    insert_data.update({
                        'daily_predictions': predictions['predictions'],
                        'prediction_dates': [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in predictions['dates']]
                    })
                
                # Calculate and add trend analysis
                trend_data = self._analyze_ec_trend(predictions)
                insert_data.update(trend_data)
                
                # Calculate and add readiness estimation
                readiness_data = self._calculate_readiness_metrics(ec, moisture, predictions)
                insert_data.update(readiness_data)
                
                # Calculate condition assessments
                condition_data = self._assess_compost_conditions(ec, moisture, stats)
                insert_data.update(condition_data)
                
                # Generate recommendations
                recommendation_data = self._generate_recommendations(ec, moisture, predictions)
                insert_data.update(recommendation_data)
                
                # Calculate dashboard metrics
                dashboard_data = self._calculate_dashboard_metrics(ec, moisture, predictions)
                insert_data.update(dashboard_data)
                
            else:
                # Handle prediction failure
                insert_data.update({
                    'prediction_generated': True,
                    'prediction_success': False,
                    'prediction_error': predictions.get('error', 'Unknown prediction error'),
                    'forecast_date': datetime.now().isoformat()
                })
            
            response = self.supabase.table('compost_status').insert(insert_data).execute()
            
            if response.data:
                logger.info(f"Created comprehensive compost status for user {telegram_id}: EC={ec}, Moisture={moisture}, Predictions={'✅' if predictions.get('success') else '❌'}")
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating compost status with predictions for telegram_id {telegram_id}: {e}")
            return None
    
    def _analyze_ec_trend(self, predictions: Dict) -> Dict[str, Any]:
        """Analyze EC trend from predictions"""
        try:
            current_ec = predictions['statistics']['current_ec']
            final_ec = predictions['key_predictions']['month_3']
            
            # Calculate trend
            change_ratio = final_ec / current_ec if current_ec > 0 else 1
            
            if change_ratio > 1.2:
                trend = 'rising'
                strength = min((change_ratio - 1) * 2, 1.0)  # Scale to 0-1
            elif change_ratio < 0.8:
                trend = 'declining' 
                strength = min((1 - change_ratio) * 2, 1.0)
            else:
                trend = 'stable'
                strength = 1 - abs(change_ratio - 1) * 5  # Higher is more stable
            
            return {
                'ec_trend': trend,
                'trend_strength': round(strength, 3),
                'trend_description': f"EC is {trend} from {current_ec} to {final_ec} mS/cm over 90 days"
            }
        except:
            return {'ec_trend': 'unknown', 'trend_strength': 0, 'trend_description': 'Unable to analyze trend'}
    
    def _calculate_readiness_metrics(self, ec: float, moisture: float, predictions: Dict) -> Dict[str, Any]:
        """Calculate compost readiness metrics"""
        try:
            # Analyze EC predictions for readiness
            preds = predictions.get('predictions', [])
            optimal_min, optimal_max = 1.5, 3.0
            
            # Find when compost reaches optimal range
            readiness_day = None
            consecutive_optimal = 0
            
            for i, pred_ec in enumerate(preds):
                if optimal_min <= pred_ec <= optimal_max:
                    consecutive_optimal += 1
                    if consecutive_optimal >= 7 and readiness_day is None:
                        readiness_day = i + 1
                        break
                else:
                    consecutive_optimal = 0
            
            # Determine readiness status and confidence
            if readiness_day is not None:
                if readiness_day <= 14:
                    status = 'ready_soon'
                    confidence = 'high'
                elif readiness_day <= 30:
                    status = 'short_term'
                    confidence = 'high'
                elif readiness_day <= 60:
                    status = 'medium_term'
                    confidence = 'medium'
                else:
                    status = 'long_term'
                    confidence = 'medium'
            else:
                status = 'needs_attention'
                confidence = 'low'
                readiness_day = None
            
            # Determine maturity stage
            if ec < 1.0:
                stage = 'building_nutrients'
            elif ec > 4.0:
                stage = 'active_decomposition'
            elif 1.5 <= ec <= 3.0:
                stage = 'stabilizing' if consecutive_optimal < 7 else 'nearly_ready'
            else:
                stage = 'active_decomposition'
            
            ready_date = None
            if readiness_day:
                from datetime import timedelta
                ready_date = (datetime.now() + timedelta(days=readiness_day)).isoformat()
            
            return {
                'readiness_status': status,
                'estimated_ready_days': readiness_day,
                'estimated_ready_date': ready_date,
                'readiness_confidence': confidence,
                'current_maturity_stage': stage
            }
        except:
            return {
                'readiness_status': 'unknown',
                'readiness_confidence': 'low',
                'current_maturity_stage': 'unknown'
            }
    
    def _assess_compost_conditions(self, ec: float, moisture: float, stats: Dict) -> Dict[str, Any]:
        """Assess current compost conditions"""
        try:
            # EC status assessment
            if ec < 1.0:
                ec_status = 'low'
            elif 1.5 <= ec <= 3.0:
                ec_status = 'optimal'
            elif 3.0 < ec <= 5.0:
                ec_status = 'high'
            else:
                ec_status = 'very_high'
            
            # Moisture status assessment
            if moisture < 40:
                moisture_status = 'low'
            elif 45 <= moisture <= 65:
                moisture_status = 'optimal'
            elif 65 < moisture <= 80:
                moisture_status = 'high'
            else:
                moisture_status = 'very_high'
            
            # Calculate overall health score (0-100)
            ec_score = 100 if ec_status == 'optimal' else (70 if ec_status in ['low', 'high'] else 40)
            moisture_score = 100 if moisture_status == 'optimal' else (70 if moisture_status in ['low', 'high'] else 40)
            trend_score = 80  # Default, could be enhanced with trend analysis
            
            health_score = round((ec_score + moisture_score + trend_score) / 3)
            
            # Health description
            if health_score >= 85:
                health_desc = "Excellent conditions - compost is thriving"
            elif health_score >= 70:
                health_desc = "Good conditions - minor adjustments may help"
            elif health_score >= 50:
                health_desc = "Fair conditions - some attention needed"
            else:
                health_desc = "Poor conditions - immediate action required"
            
            return {
                'ec_status': ec_status,
                'moisture_status': moisture_status,
                'overall_health_score': health_score,
                'health_description': health_desc
            }
        except:
            return {
                'ec_status': 'unknown',
                'moisture_status': 'unknown',
                'overall_health_score': 50,
                'health_description': 'Unable to assess conditions'
            }
    
    def _generate_recommendations(self, ec: float, moisture: float, predictions: Dict) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        try:
            recommendations = {}
            
            # Primary recommendation based on EC
            if ec < 1.0:
                recommendations['primary_recommendation'] = "Add nitrogen-rich materials (kitchen scraps, grass clippings) to boost nutrient levels"
                recommendations['nutrient_recommendation'] = "Increase nitrogen inputs - add fresh organic matter"
            elif ec > 4.0:
                recommendations['primary_recommendation'] = "Allow current materials to decompose - avoid adding more inputs temporarily"
                recommendations['nutrient_recommendation'] = "No additional nutrients needed - let existing materials stabilize"
            elif 1.5 <= ec <= 3.0:
                recommendations['primary_recommendation'] = "Maintain current management - conditions are optimal"
                recommendations['nutrient_recommendation'] = "Nutrient levels are balanced - continue current inputs"
            else:
                recommendations['primary_recommendation'] = "Monitor closely and adjust inputs based on EC trends"
                recommendations['nutrient_recommendation'] = "Fine-tune nutrient balance based on ongoing measurements"
            
            # Moisture recommendation
            if moisture < 40:
                recommendations['moisture_recommendation'] = "Increase watering - aim for 45-65% moisture"
            elif moisture > 70:
                recommendations['moisture_recommendation'] = "Reduce watering and improve drainage - aim for 45-65% moisture"
            else:
                recommendations['moisture_recommendation'] = "Moisture levels are good - maintain current watering schedule"
            
            # Timeline recommendation
            trend = predictions.get('statistics', {}).get('current_ec', ec)
            final_ec = predictions.get('key_predictions', {}).get('month_3', ec)
            
            if abs(final_ec - 2.25) < 0.5:  # Close to optimal center
                recommendations['timeline_recommendation'] = "On track for good quality compost in 2-3 months"
            else:
                recommendations['timeline_recommendation'] = "Monitor progress and adjust management as needed"
            
            # Secondary recommendation
            recommendations['secondary_recommendation'] = "Turn compost weekly and monitor temperature for optimal decomposition"
            
            return recommendations
        except:
            return {
                'primary_recommendation': 'Monitor conditions and adjust as needed',
                'secondary_recommendation': 'Continue regular maintenance',
                'nutrient_recommendation': 'Balance organic inputs based on observations',
                'moisture_recommendation': 'Maintain adequate moisture levels',
                'timeline_recommendation': 'Allow natural decomposition process'
            }
    
    def _calculate_dashboard_metrics(self, ec: float, moisture: float, predictions: Dict) -> Dict[str, Any]:
        """Calculate metrics specifically for dashboard display"""
        try:
            metrics = {}
            
            # Completion percentage (0-100) based on EC position in optimal range
            if 1.5 <= ec <= 3.0:
                # In optimal range - calculate based on stability
                metrics['completion_percentage'] = min(85, 60 + (ec - 1.5) * 20)
            elif ec < 1.5:
                # Building nutrients
                metrics['completion_percentage'] = max(10, ec * 40)
            else:
                # Too high - needs to come down
                metrics['completion_percentage'] = max(20, 100 - (ec - 3.0) * 15)
            
            # Quality score (0-10) based on conditions
            ec_quality = 10 if 1.5 <= ec <= 3.0 else (7 if 1.0 <= ec <= 4.0 else 4)
            moisture_quality = 10 if 45 <= moisture <= 65 else (7 if 30 <= moisture <= 80 else 4)
            metrics['quality_score'] = round((ec_quality + moisture_quality) / 2, 1)
            
            # Stability index (0-10) based on how predictable conditions are
            if predictions.get('success'):
                pred_variance = 0
                preds = predictions.get('predictions', [])
                if len(preds) > 10:
                    # Calculate variance in first 30 days
                    early_preds = preds[:30]
                    avg_pred = sum(early_preds) / len(early_preds)
                    variance = sum((p - avg_pred) ** 2 for p in early_preds) / len(early_preds)
                    pred_variance = min(variance, 2.0)  # Cap at 2.0
                
                metrics['stability_index'] = round(max(1, 10 - pred_variance * 3), 1)
            else:
                metrics['stability_index'] = 5.0
            
            # Days in optimal range (next 30 days)
            optimal_days = 0
            if predictions.get('success'):
                preds = predictions.get('predictions', [])[:30]  # Next 30 days
                optimal_days = sum(1 for p in preds if 1.5 <= p <= 3.0)
            
            metrics['optimal_range_days'] = optimal_days
            
            # Alert system
            if ec > 6.0 or moisture > 85:
                metrics['alert_level'] = 'critical'
                metrics['alert_message'] = 'Immediate attention required - conditions are extreme'
                metrics['action_required'] = True
            elif ec > 4.0 or moisture < 30 or moisture > 75:
                metrics['alert_level'] = 'warning'
                metrics['alert_message'] = 'Conditions need adjustment'
                metrics['action_required'] = True
            elif ec < 1.0:
                metrics['alert_level'] = 'info'
                metrics['alert_message'] = 'Consider adding more organic material'
                metrics['action_required'] = False
            else:
                metrics['alert_level'] = 'none'
                metrics['alert_message'] = None
                metrics['action_required'] = False
            
            # Next check recommendation
            from datetime import timedelta
            if metrics['alert_level'] == 'critical':
                next_check = datetime.now() + timedelta(days=1)
            elif metrics['alert_level'] == 'warning':
                next_check = datetime.now() + timedelta(days=3)
            else:
                next_check = datetime.now() + timedelta(days=7)
            
            metrics['next_check_date'] = next_check.isoformat()
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating dashboard metrics: {e}")
            return {
                'completion_percentage': 50,
                'quality_score': 5.0,
                'stability_index': 5.0,
                'optimal_range_days': 15,
                'alert_level': 'none',
                'action_required': False
            }
    
    def get_user_compost_status_history(self, telegram_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent compost status entries for a user
        
        Args:
            telegram_id: User's telegram ID
            limit: Maximum number of records to return
            
        Returns:
            List of compost status records
        """
        try:
            response = self.supabase.table('compost_status').select("*").eq(
                'telegram_id', telegram_id
            ).order('created_at', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting compost status history for telegram_id {telegram_id}: {e}")
            return []
    
    def get_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user including latest status, trends, and predictions
        
        Args:
            telegram_id: User's telegram ID
            
        Returns:
            Dictionary containing dashboard data
        """
        try:
            # Get latest status with predictions
            latest_response = self.supabase.table('compost_status').select("*").eq(
                'telegram_id', telegram_id
            ).eq('prediction_generated', True).order('created_at', desc=True).limit(1).execute()
            
            latest_status = latest_response.data[0] if latest_response.data else None
            
            # Get historical data (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            history_response = self.supabase.table('compost_status').select("*").eq(
                'telegram_id', telegram_id
            ).gte('created_at', thirty_days_ago).order('created_at', desc=True).execute()
            
            history = history_response.data if history_response.data else []
            
            # Calculate dashboard metrics
            dashboard_data = {
                'latest_status': latest_status,
                'history_30_days': history,
                'summary': self._calculate_dashboard_summary(latest_status, history),
                'alerts': self._get_active_alerts(latest_status),
                'recommendations': self._get_current_recommendations(latest_status),
                'charts_data': self._prepare_charts_data(latest_status, history)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for telegram_id {telegram_id}: {e}")
            return {
                'latest_status': None,
                'history_30_days': [],
                'summary': {},
                'alerts': [],
                'recommendations': {},
                'charts_data': {}
            }
    
    def _calculate_dashboard_summary(self, latest: Dict, history: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for dashboard"""
        if not latest:
            return {}
        
        try:
            summary = {
                'current_ec': latest.get('ec', 0),
                'current_moisture': latest.get('moisture', 0),
                'readiness_status': latest.get('readiness_status', 'unknown'),
                'estimated_ready_days': latest.get('estimated_ready_days'),
                'completion_percentage': latest.get('completion_percentage', 0),
                'quality_score': latest.get('quality_score', 0),
                'health_score': latest.get('overall_health_score', 0),
                'trend': latest.get('ec_trend', 'unknown'),
                'days_monitored': len(history),
                'last_updated': latest.get('created_at')
            }
            
            # Calculate improvements over time
            if len(history) > 1:
                oldest = history[-1]
                ec_change = latest.get('ec', 0) - oldest.get('ec', 0)
                summary['ec_change_30_days'] = round(ec_change, 2)
                summary['improving_trend'] = ec_change > 0 if oldest.get('ec', 0) < 2.25 else ec_change < 0
            
            return summary
        except:
            return {'error': 'Unable to calculate summary'}
    
    def _get_active_alerts(self, latest: Dict) -> List[Dict[str, Any]]:
        """Get active alerts for dashboard"""
        if not latest:
            return []
        
        alerts = []
        
        # Add current alert if exists
        if latest.get('alert_level') != 'none' and latest.get('alert_message'):
            alerts.append({
                'level': latest.get('alert_level'),
                'message': latest.get('alert_message'),
                'action_required': latest.get('action_required', False),
                'created_at': latest.get('created_at')
            })
        
        # Check for specific conditions
        ec = latest.get('ec', 0)
        moisture = latest.get('moisture', 0)
        
        if latest.get('estimated_ready_days') and latest.get('estimated_ready_days') <= 7:
            alerts.append({
                'level': 'info',
                'message': f"🎉 Compost will be ready in ~{latest.get('estimated_ready_days')} days!",
                'action_required': False,
                'created_at': latest.get('created_at')
            })
        
        return alerts
    
    def _get_current_recommendations(self, latest: Dict) -> Dict[str, Any]:
        """Get current recommendations for dashboard"""
        if not latest:
            return {}
        
        return {
            'primary': latest.get('primary_recommendation'),
            'secondary': latest.get('secondary_recommendation'),
            'nutrient': latest.get('nutrient_recommendation'),
            'moisture': latest.get('moisture_recommendation'),
            'timeline': latest.get('timeline_recommendation'),
            'next_check': latest.get('next_check_date')
        }
    
    def _prepare_charts_data(self, latest: Dict, history: List[Dict]) -> Dict[str, Any]:
        """Prepare data for dashboard charts"""
        charts_data = {}
        
        try:
            # Historical EC trend chart
            if history:
                charts_data['ec_history'] = {
                    'dates': [record.get('created_at') for record in reversed(history)],
                    'values': [record.get('ec', 0) for record in reversed(history)]
                }
                
                charts_data['moisture_history'] = {
                    'dates': [record.get('created_at') for record in reversed(history)],
                    'values': [record.get('moisture', 0) for record in reversed(history)]
                }
            
            # Future predictions chart
            if latest and latest.get('daily_predictions'):
                charts_data['predictions'] = {
                    'dates': latest.get('prediction_dates', []),
                    'values': latest.get('daily_predictions', [])
                }
            
            # Readiness timeline
            if latest and latest.get('estimated_ready_days'):
                from datetime import datetime, timedelta
                ready_date = datetime.now() + timedelta(days=latest.get('estimated_ready_days'))
                charts_data['readiness_timeline'] = {
                    'current_date': datetime.now().isoformat(),
                    'ready_date': ready_date.isoformat(),
                    'days_remaining': latest.get('estimated_ready_days'),
                    'completion_percentage': latest.get('completion_percentage', 0)
                }
            
        except Exception as e:
            logger.error(f"Error preparing charts data: {e}")
        
        return charts_data

db = DatabaseService()