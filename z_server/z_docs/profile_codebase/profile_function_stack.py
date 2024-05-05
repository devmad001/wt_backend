import cProfile
import pstats

def my_function():
    # Your code here

cProfile.run('my_function()', 'profile_stats')

p = pstats.Stats('profile_stats')
p.sort_stats('cumulative').print_stats(10)  # Prints the top 10 by cumulative time
