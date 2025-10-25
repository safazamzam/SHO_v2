"""
Example Usage of Shift Configuration Service

This file demonstrates how to use the ShiftConfigService to get shift timing and timezone 
configurations from the database instead of hardcoded values.
"""

from services.shift_config_service import shift_config_service
from datetime import datetime, time

# Example 1: Get current timezone
def example_get_timezone():
    """Get the configured application timezone"""
    app_timezone = shift_config_service.get_timezone()
    current_time = datetime.now(app_timezone)
    
    print(f"Application timezone: {app_timezone}")
    print(f"Current time in app timezone: {current_time}")
    return app_timezone

# Example 2: Get shift timings
def example_get_shift_times():
    """Get all shift timing configurations"""
    shift_times = shift_config_service.get_shift_times()
    
    print("Current shift timing configuration:")
    for shift_name, config in shift_times.items():
        print(f"  {config['name']} Shift ({config['code']}): {config['start']} - {config['end']}")
    
    return shift_times

# Example 3: Determine current shift
def example_current_shift():
    """Determine what shift we're currently in"""
    current_shift, next_shift = shift_config_service.get_current_shift_type()
    
    print(f"Current shift: {current_shift}")
    print(f"Next shift: {next_shift}")
    
    return current_shift, next_shift

# Example 4: Get shift times as time objects for comparison
def example_time_comparison():
    """Use shift times for time-based logic"""
    shift_times = shift_config_service.get_shift_times_as_time_objects()
    current_time = datetime.now().time()
    
    print(f"Current time: {current_time}")
    
    for shift_name, config in shift_times.items():
        start_time = config['start']
        end_time = config['end']
        
        # Example logic for checking if current time is within shift
        if shift_name == 'night':
            # Night shift crosses midnight, needs special handling
            if start_time <= current_time or current_time < end_time:
                print(f"Currently in {config['name']} shift")
        else:
            if start_time <= current_time < end_time:
                print(f"Currently in {config['name']} shift")

# Usage in existing routes (example for routes/dashboard.py)
def updated_dashboard_shift_logic():
    """
    Example of how to update existing hardcoded shift logic
    
    OLD CODE:
    def get_shift_type_and_next(now):
        t = now.time()
        if dt_time(6,30) <= t < dt_time(15,30):
            return 'Morning', 'Evening'
        elif dt_time(14,45) <= t < dt_time(23,45):
            return 'Evening', 'Night'
        else:
            return 'Night', 'Morning'
    
    NEW CODE:
    """
    from services.shift_config_service import shift_config_service
    
    def get_shift_type_and_next(now=None):
        """Get current and next shift types using database configuration"""
        return shift_config_service.get_current_shift_type(now)

# Usage in CTask assignment service
def updated_ctask_shift_logic():
    """
    Example of how to update CTask assignment service to use configurable shift times
    
    OLD CODE (hardcoded):
    self.shift_times = {
        'D': {'start_time': time(6, 30), 'end_time': time(15, 30), 'name': 'Day/Morning'},
        'E': {'start_time': time(14, 45), 'end_time': time(23, 45), 'name': 'Evening'},
        'N': {'start_time': time(21, 45), 'end_time': time(6, 45), 'name': 'Night'}
    }
    
    NEW CODE (configurable):
    """
    from services.shift_config_service import shift_config_service
    
    def __init__(self):
        # Get shift times from database configuration
        self.shift_times = {}
        configured_times = shift_config_service.get_shift_times_as_time_objects()
        
        for shift_name, config in configured_times.items():
            self.shift_times[config['code']] = {
                'start_time': config['start'],
                'end_time': config['end'], 
                'name': config['name']
            }

if __name__ == "__main__":
    print("=== Shift Configuration Service Examples ===\n")
    
    print("1. Getting timezone configuration:")
    example_get_timezone()
    
    print("\n2. Getting shift timing configuration:")
    example_get_shift_times()
    
    print("\n3. Determining current shift:")
    example_current_shift()
    
    print("\n4. Time comparison example:")
    example_time_comparison()