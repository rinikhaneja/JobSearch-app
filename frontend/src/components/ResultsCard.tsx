import React from 'react';
import { Card, CardContent, Typography, Box, Chip, CircularProgress } from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import WorkIcon from '@mui/icons-material/Work';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import { UploadResults, AnalysisResponse } from '../types/jobsearch';

interface Job {
  job_id: string;
  job_title: string;
  cmp_name: string;
  city: string;
  state: string;
  country: string;
  description: string;
  qualification_required: string;
  skills_required: string[];
  salary_offered?: string;
  posted_date?: string;
}

interface GeneralResults {
  message: string;
  path?: string;
  size?: string;
  type?: string;
  user_id?: string;
  session_id?: string;
}

interface ResultsCardProps {
  // For job results
  jobs?: Job[];
  loading?: boolean;
  // For general results
  results?: GeneralResults;
  // For upload results
  uploadResults?: UploadResults;
  // For analysis results
  analysisResults?: AnalysisResponse;
}

/**
 * A unified component that can display either job search results or general results
 * (like upload/analysis results) based on the props provided.
 */
const ResultsCard: React.FC<ResultsCardProps> = ({ jobs, loading, results, uploadResults, analysisResults }) => {
  // Handle job results display
  if (jobs !== undefined) {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      );
    }

    if (!jobs || jobs.length === 0) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <Typography variant="h6" color="textSecondary">
            No jobs found. Try adjusting your search criteria.
          </Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {jobs.map((job) => (
          <Card key={job.job_id} elevation={2} sx={{ 
            '&:hover': { 
              boxShadow: 6,
              transform: 'translateY(-2px)',
              transition: 'all 0.3s ease'
            }
          }}>
            <CardContent>
              <Typography variant="h5" gutterBottom color="primary">
                {job.job_title}
              </Typography>
              
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <BusinessIcon color="action" fontSize="small" />
                <Typography variant="subtitle1" color="textSecondary">
                  {job.cmp_name}
                </Typography>
              </Box>

              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <LocationOnIcon color="action" fontSize="small" />
                <Typography variant="body2" color="textSecondary">
                  {[job.city, job.state, job.country].filter(Boolean).join(', ')}
                </Typography>
              </Box>

              {job.salary_offered && (
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <WorkIcon color="action" fontSize="small" />
                  <Typography variant="body2" color="textSecondary">
                    {job.salary_offered}
                  </Typography>
                </Box>
              )}

              {job.posted_date && (
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <AccessTimeIcon color="action" fontSize="small" />
                  <Typography variant="body2" color="textSecondary">
                    Posted: {new Date(job.posted_date).toLocaleDateString()}
                  </Typography>
                </Box>
              )}

              <Typography variant="body2" paragraph>
                {job.description?.slice(0, 200)}...
              </Typography>

              {job.skills_required && job.skills_required.length > 0 && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Required Skills:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {job.skills_required.map((skill, index) => (
                      <Chip
                        key={index}
                        label={skill}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {job.qualification_required && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Qualifications:
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {job.qualification_required}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  // Handle general results display
  if (results) {
    console.info('ResultsCard component rendered with results:', results);
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Results</Typography>
          <Typography variant="body1">{results.message}</Typography>
          {results.path && <Typography variant="body2">Path: {results.path}</Typography>}
          {results.size && <Typography variant="body2">Size: {results.size}</Typography>}
          {results.type && <Typography variant="body2">Type: {results.type}</Typography>}
          {results.user_id && <Typography variant="body2">User ID: {results.user_id}</Typography>}
          {results.session_id && <Typography variant="body2">Session ID: {results.session_id}</Typography>}
        </CardContent>
      </Card>
    );
  }

  // Handle upload results display
  if (uploadResults) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload Results
          </Typography>
          <Typography color="textSecondary" gutterBottom>
            {uploadResults.message}
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>File Path:</strong> {uploadResults.path}
            </Typography>
            <Typography variant="body2">
              <strong>File Size:</strong> {uploadResults.size}
            </Typography>
            <Typography variant="body2">
              <strong>File Type:</strong> {uploadResults.type}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Handle analysis results display
  if (analysisResults) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Analysis Results
          </Typography>
          <Typography color="textSecondary" gutterBottom>
            {analysisResults.message}
          </Typography>
          <Box sx={{ mt: 2 }}>
            {analysisResults.extracted_info.name && (
              <Typography variant="body2">
                <strong>Name:</strong> {analysisResults.extracted_info.name}
              </Typography>
            )}
            {analysisResults.extracted_info.email && (
              <Typography variant="body2">
                <strong>Email:</strong> {analysisResults.extracted_info.email}
              </Typography>
            )}
            {analysisResults.extracted_info.phone && (
              <Typography variant="body2">
                <strong>Phone:</strong> {analysisResults.extracted_info.phone}
              </Typography>
            )}
            {analysisResults.extracted_info.skills && analysisResults.extracted_info.skills.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" gutterBottom>
                  <strong>Skills:</strong>
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {analysisResults.extracted_info.skills.map((skill, index) => (
                    <Chip key={index} label={skill} size="small" />
                  ))}
                </Box>
              </Box>
            )}
            {analysisResults.extracted_info.experience && analysisResults.extracted_info.experience.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" gutterBottom>
                  <strong>Experience:</strong>
                </Typography>
                {analysisResults.extracted_info.experience.map((exp, index) => (
                  <Typography key={index} variant="body2">
                    {exp}
                  </Typography>
                ))}
              </Box>
            )}
            {analysisResults.extracted_info.education && analysisResults.extracted_info.education.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" gutterBottom>
                  <strong>Education:</strong>
                </Typography>
                {analysisResults.extracted_info.education.map((edu, index) => (
                  <Typography key={index} variant="body2">
                    {edu}
                  </Typography>
                ))}
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Fallback if neither jobs, general results, upload results, nor analysis results are provided
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
      <Typography variant="h6" color="textSecondary">
        No results to display
      </Typography>
    </Box>
  );
};

export default ResultsCard; 