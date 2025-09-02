#!/usr/bin/env python3
"""
Analytics service for KE-ROUMA app usage tracking and insights
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from models.database import get_database
import json

class AnalyticsService:
    """Service for tracking user interactions and app performance"""
    
    @staticmethod
    async def track_event(event_type: str, user_id: str = None, data: Dict[str, Any] = None):
        """Track user event"""
        try:
            db = await get_database()
            
            event = {
                "event_type": event_type,
                "user_id": user_id,
                "data": data or {},
                "timestamp": datetime.utcnow(),
                "session_id": data.get("session_id") if data else None
            }
            
            await db.analytics_events.insert_one(event)
            
        except Exception as e:
            print(f"Analytics tracking error: {e}")
    
    @staticmethod
    async def track_recipe_generation(user_id: str, provider: str, ingredients: List[str], 
                                    generation_time: float, success: bool):
        """Track recipe generation events"""
        await AnalyticsService.track_event("recipe_generation", user_id, {
            "provider": provider,
            "ingredient_count": len(ingredients),
            "ingredients": ingredients,
            "generation_time": generation_time,
            "success": success
        })
    
    @staticmethod
    async def track_payment(user_id: str, amount: float, payment_type: str, success: bool):
        """Track payment events"""
        await AnalyticsService.track_event("payment", user_id, {
            "amount": amount,
            "payment_type": payment_type,
            "success": success
        })
    
    @staticmethod
    async def track_api_usage(user_id: str, endpoint: str, response_time: float, status_code: int):
        """Track API endpoint usage"""
        await AnalyticsService.track_event("api_usage", user_id, {
            "endpoint": endpoint,
            "response_time": response_time,
            "status_code": status_code
        })
    
    @staticmethod
    async def get_user_stats(user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user activity statistics"""
        try:
            db = await get_database()
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$event_type",
                        "count": {"$sum": 1},
                        "last_activity": {"$max": "$timestamp"}
                    }
                }
            ]
            
            results = await db.analytics_events.aggregate(pipeline).to_list(length=None)
            
            stats = {
                "user_id": user_id,
                "period_days": days,
                "events": {result["_id"]: result["count"] for result in results},
                "last_activities": {result["_id"]: result["last_activity"] for result in results}
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
    
    @staticmethod
    async def get_app_metrics(days: int = 7) -> Dict[str, Any]:
        """Get overall app performance metrics"""
        try:
            db = await get_database()
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Active users
            active_users = await db.analytics_events.distinct("user_id", {
                "timestamp": {"$gte": start_date}
            })
            
            # Recipe generation stats
            recipe_pipeline = [
                {
                    "$match": {
                        "event_type": "recipe_generation",
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$data.provider",
                        "count": {"$sum": 1},
                        "avg_time": {"$avg": "$data.generation_time"},
                        "success_rate": {
                            "$avg": {"$cond": ["$data.success", 1, 0]}
                        }
                    }
                }
            ]
            
            recipe_stats = await db.analytics_events.aggregate(recipe_pipeline).to_list(length=None)
            
            # Payment stats
            payment_pipeline = [
                {
                    "$match": {
                        "event_type": "payment",
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_amount": {"$sum": "$data.amount"},
                        "transaction_count": {"$sum": 1},
                        "success_rate": {
                            "$avg": {"$cond": ["$data.success", 1, 0]}
                        }
                    }
                }
            ]
            
            payment_stats = await db.analytics_events.aggregate(payment_pipeline).to_list(length=1)
            
            return {
                "period_days": days,
                "active_users": len(active_users),
                "recipe_generation": {
                    stat["_id"]: {
                        "count": stat["count"],
                        "avg_time": round(stat["avg_time"], 2),
                        "success_rate": round(stat["success_rate"] * 100, 1)
                    }
                    for stat in recipe_stats
                },
                "payments": payment_stats[0] if payment_stats else {},
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error getting app metrics: {e}")
            return {}
    
    @staticmethod
    async def get_popular_ingredients(days: int = 30, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular ingredients used in recipes"""
        try:
            db = await get_database()
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "event_type": "recipe_generation",
                        "timestamp": {"$gte": start_date},
                        "data.success": True
                    }
                },
                {
                    "$unwind": "$data.ingredients"
                },
                {
                    "$group": {
                        "_id": {"$toLower": "$data.ingredients"},
                        "count": {"$sum": 1},
                        "users": {"$addToSet": "$user_id"}
                    }
                },
                {
                    "$project": {
                        "ingredient": "$_id",
                        "usage_count": "$count",
                        "user_count": {"$size": "$users"}
                    }
                },
                {
                    "$sort": {"usage_count": -1}
                },
                {
                    "$limit": limit
                }
            ]
            
            results = await db.analytics_events.aggregate(pipeline).to_list(length=None)
            return results
            
        except Exception as e:
            print(f"Error getting popular ingredients: {e}")
            return []

# Performance monitoring
class PerformanceMonitor:
    """Monitor app performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    async def record_response_time(self, endpoint: str, time_ms: float):
        """Record API response time"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        
        self.metrics[endpoint].append({
            "time_ms": time_ms,
            "timestamp": datetime.utcnow()
        })
        
        # Keep only last 1000 entries per endpoint
        if len(self.metrics[endpoint]) > 1000:
            self.metrics[endpoint] = self.metrics[endpoint][-1000:]
    
    def get_performance_stats(self, endpoint: str = None) -> Dict[str, Any]:
        """Get performance statistics"""
        if endpoint:
            if endpoint not in self.metrics:
                return {}
            
            times = [m["time_ms"] for m in self.metrics[endpoint]]
            return {
                "endpoint": endpoint,
                "avg_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "request_count": len(times)
            }
        
        # Return stats for all endpoints
        stats = {}
        for ep, data in self.metrics.items():
            times = [m["time_ms"] for m in data]
            stats[ep] = {
                "avg_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "request_count": len(times)
            }
        
        return stats

# Global performance monitor
performance_monitor = PerformanceMonitor()
