from flock import FlockDict

pycon_stats = FlockDict()
pycon_stats["attendees"] = 2800
pycon_stats["talks"] = 80
pycon_stats["sponsors"] = 100
pycon_stats["talk_ratio"] = lambda: pycon_stats["attendees"] / pycon_stats["talks"]
pycon_stats["sponsor_ratio"] = (
    lambda: pycon_stats["attendees"] / pycon_stats["sponsors"]
)
