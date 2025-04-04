#!/usr/bin/env python3
"""
Test script for Word Counter CLI
"""
import os
import sys
import unittest

# Add parent directory to path to import wordcounter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import wordcounter

class TestWordCounter(unittest.TestCase):
    """Tests for the Word Counter CLI application."""
    
    def setUp(self):
        """Set up test files paths."""
        self.sample1_path = os.path.join(os.path.dirname(__file__), 'sample1.txt')
        self.sample2_path = os.path.join(os.path.dirname(__file__), 'sample2.md')
    
    def test_count_file_stats_txt(self):
        """Test counting stats for a text file."""
        stats = wordcounter.count_file_stats(self.sample1_path)
        
        # Check results (based on sample1.txt content)
        self.assertEqual(stats['words'], 57)
        self.assertEqual(stats['lines'], 13)
        self.assertEqual(stats['paragraphs'], 4)
        # Character count may vary slightly depending on line endings
        self.assertTrue(stats['characters'] > 250)
    
    def test_count_file_stats_md(self):
        """Test counting stats for a markdown file."""
        stats = wordcounter.count_file_stats(self.sample2_path)
        
        # Check results (based on sample2.md content)
        self.assertEqual(stats['words'], 70)
        self.assertEqual(stats['paragraphs'], 7)
        # Other counts may vary slightly
    
    def test_ignore_spaces(self):
        """Test the ignore_spaces flag."""
        stats_with_spaces = wordcounter.count_file_stats(self.sample1_path)
        stats_without_spaces = wordcounter.count_file_stats(self.sample1_path, ignore_spaces=True)
        
        # Character count without spaces should be less than with spaces
        self.assertTrue(stats_without_spaces['characters'] < stats_with_spaces['characters'])
    
    def test_analyze_multiple_files(self):
        """Test analyzing multiple files."""
        results = wordcounter.analyze_files([self.sample1_path, self.sample2_path])
        
        # Check that we have results for both files and a total
        self.assertEqual(len(results), 3)
        self.assertTrue(self.sample1_path in results)
        self.assertTrue(self.sample2_path in results)
        self.assertTrue('TOTAL' in results)
        
        # Check that totals are the sum of individual files
        total = results['TOTAL']
        self.assertEqual(total['words'], 
                         results[self.sample1_path]['words'] + results[self.sample2_path]['words'])

if __name__ == "__main__":
    unittest.main()
