"""Pytest configuration and global fixtures."""

import matplotlib
# Use the non-interactive Agg backend for testing to prevent GUI windows
# from opening or hanging during test execution.
matplotlib.use("Agg")
