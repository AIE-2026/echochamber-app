# core/metrics.py
# ================
# Pure metric functions and chart generators.
# No Gradio here — these are testable independently.
#
# Functions:
#   compute_dissimilarity(a, b)          → float  (0=identical, 1=no overlap)
#   lexical_diversity(text)              → float  (Type-Token Ratio)
#   compute_sentiment(text)              → float  (-0.1 .. +0.1)
#   render_agent_metrics(responses, agents, neutral_summary) → HTML string
#   render_debate_stats(messages, agents, active_slugs)      → HTML string
#   plot_sentiment_timeline(messages)    → matplotlib Figure
#   plot_dissimilarity_bars(responses, agents, neutral)      → matplotlib Figure
#   plot_sentiment_bars(responses, agents)                   → matplotlib Figure
#   plot_debate_sentiment_line(messages) → matplotlib Figure
#
# Students: you can extend this file with new metrics.
# A good experiment: add a "populism score" based on a custom lexicon.
