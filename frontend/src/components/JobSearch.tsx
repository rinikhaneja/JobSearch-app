import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, CircularProgress, Alert, Paper, Fade, TextField } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import JobSearchResults from './JobSearchResults';
import { Job } from '../types/jobsearch';

interface JobSearchProps {
  user_id: string;
  session_id: string;
  current_job_title?: string;
  jobs?: Job[];
}

const JobSearch: React.FC<JobSearchProps> = ({ user_id, session_id, current_job_title, jobs = [] }) => {
  const [searching, setSearching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [jobTitle, setJobTitle] = useState<string>('');
  const [location, setLocation] = useState<string>('United States');
  const [searchResults, setSearchResults] = useState<Job[]>(jobs);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUserDetails = async () => {
      if (!user_id || !session_id) return;

      try {
        const url = `http://localhost:8000/user-details/${user_id}?session_id=${session_id}`;
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          const errorData = await response.json();
          if (errorData instanceof Error) {
            setError(errorData.message);
          } else if (typeof errorData === 'object' && errorData !== null && 'detail' in errorData) {
            setError(JSON.stringify(errorData.detail));
          } else {
            setError('Failed to fetch user details');
          }
        }

        const data = await response.json();
        if (data.current_job_title) {
          setJobTitle(data.current_job_title);
        }
      } catch (error) {
        console.error('Error fetching user details:', error);
        if (error instanceof Error) {
          setError(error.message);
        } else if (typeof error === 'object' && error !== null && 'detail' in error) {
          setError(JSON.stringify(error.detail));
        } else {
          setError('Failed to fetch user details');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUserDetails();
  }, [user_id, session_id]);

  const handleJobSearch = async () => {
    if (!user_id || !session_id) {
      setError('User session not found. Please upload your resume first.');
      return;
    }

    if (!jobTitle.trim()) {
      setError('Please enter a job title to search');
      return;
    }

    setSearching(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/search-jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id,
          session_id,
          job_title: jobTitle.trim(),
          location,
          num_pages: 3
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to search jobs');
      }

      const data = await response.json();
      setSearchResults(Array.isArray(data) ? data : []);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to search jobs');
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Fade in timeout={500}>
      <Paper elevation={4} sx={{ maxWidth: 1200, mx: 'auto', p: 4, borderRadius: 3, boxShadow: 6 }}>
        <Typography variant="h5" gutterBottom>
          Search Jobs
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <TextField
            fullWidth
            required
            label="Job Title"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="Enter job title to search"
            error={!jobTitle.trim() && error !== null}
            helperText={!jobTitle.trim() && error !== null ? "Job title is required" : ""}
          />
          <TextField
            fullWidth
            label="Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., United States"
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Button
          variant="contained"
          color="primary"
          onClick={handleJobSearch}
          disabled={searching || !user_id || !session_id || !jobTitle.trim()}
          fullWidth
          size="large"
          sx={{ mb: 3, fontWeight: 600, letterSpacing: 1 }}
          startIcon={searching ? <CircularProgress size={22} color="inherit" /> : <SearchIcon />}
        >
          {searching ? 'Searching...' : 'Search Jobs'}
        </Button>

        {/* Job Search Results */}
        <JobSearchResults jobs={searchResults} loading={searching} />
      </Paper>
    </Fade>
  );
};

export default JobSearch; 