import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
  CircularProgress
} from '@mui/material';
import { Job } from '../types/jobsearch';

interface JobSearchResultsProps {
  jobs: Job[] | null | undefined;
  loading: boolean;
}

const JobSearchResults: React.FC<JobSearchResultsProps> = ({ jobs, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (!jobs || !Array.isArray(jobs) || jobs.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6" color="text.secondary">
          No jobs found
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ mt: 3 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Job Title</TableCell>
            <TableCell>Company</TableCell>
            <TableCell>Location</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Qualifications</TableCell>
            <TableCell>Skills</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {jobs.map((job) => (
            <TableRow key={job.job_id}>
              <TableCell>{job.job_title}</TableCell>
              <TableCell>{job.cmp_name}</TableCell>
              <TableCell>
                {[job.city, job.state, job.country]
                  .filter(Boolean)
                  .join(', ')}
              </TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ maxWidth: 300 }}>
                  {job.description}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ maxWidth: 300 }}>
                  {job.qualification_required}
                </Typography>
              </TableCell>
              <TableCell>
                <Box display="flex" flexWrap="wrap" gap={0.5}>
                  {job.skills_required?.map((skill, index) => (
                    <Chip
                      key={index}
                      label={skill}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default JobSearchResults; 