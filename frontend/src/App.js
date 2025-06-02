import React, { useState, useRef } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SearchIcon from '@mui/icons-material/Search';
import CompareIcon from '@mui/icons-material/Compare';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FolderIcon from '@mui/icons-material/Folder';

function App() {
  const [activeSection, setActiveSection] = useState(null);
  const [results, setResults] = useState(null);
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  const handleButtonClick = async (section) => {
    if (section === 'upload') {
      setOpenUploadDialog(true);
      return;
    }
    
    setActiveSection(section);
    
    switch (section) {
      case 'analyze':
        try {
          if (!uploadedFile) {
            setUploadError('Please upload a resume first');
            return;
          }

          const response = await fetch('http://localhost:8000/analyze-resume', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              filename: uploadedFile.name,
              user_id: sessionStorage.getItem('user_id'),
              session_id: sessionStorage.getItem('session_id')
            })
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze resume');
          }

          const data = await response.json();
          setResults({
            message: data.message,
            extracted_info: data.extracted_info
          });
          console.log('results:', results);
        } catch (error) {
          setUploadError(error.message || 'Failed to analyze resume');
          console.error('Analysis error:', error);
        }
        break;
      case 'search':
        setResults([
          { title: 'Senior Developer', company: 'Tech Corp', location: 'New York' },
          { title: 'Full Stack Engineer', company: 'StartUp Inc', location: 'San Francisco' }
        ]);
        break;
      case 'match':
        setResults([
          { job: 'Senior Developer', match: '95%' },
          { job: 'Full Stack Engineer', match: '85%' }
        ]);
        break;
      default:
        setResults(null);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8000/upload-resume', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to upload file');
        }

        const data = await response.json();
        setUploadedFile(file);
        setResults({
          message: `Resume uploaded successfully: ${file.name}`,
          path: data.location,
          size: `${(file.size / 1024).toFixed(2)} KB`,
          type: file.type,
          user_id: data.user_id,
          session_id: data.session_id
        });
        setActiveSection('upload');
        setUploadError(null);
        setOpenUploadDialog(false);
      } catch (error) {
        setUploadError(error.message || 'Failed to upload file. Please try again.');
        console.error('Upload error:', error);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!results?.user_id || !results?.session_id) {
      setUploadError('Please upload a resume first');
      return;
    }

    try {
      setUploadError(null);

      const response = await fetch('http://localhost:8000/analyze-resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: results.user_id,
          session_id: results.session_id
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze resume');
      }

      const data = await response.json();
      setResults({
        message: data.message,
        extracted_info: data.extracted_info
      });
      console.log('results:', results);
      setActiveSection('analysis');
    } catch (error) {
      setUploadError(error.message || 'Failed to analyze resume. Please try again.');
      console.error('Analysis error:', error);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleCloseDialog = () => {
    setOpenUploadDialog(false);
    setUploadError(null);
  };

  const renderResults = () => {
    if (!results) return null;

    switch (activeSection) {
      case 'upload':
        return (
          <Card>
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" alignItems="center" gap={2}>
                  <CheckCircleIcon color="success" />
                  <Typography variant="h6" color="success.main">
                    {results.message}
                  </Typography>
                </Box>
                <Box pl={4}>
                  <Typography variant="body2" color="textSecondary">
                    <strong>Saved to:</strong> {results.path}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    <strong>File size:</strong> {results.size}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    <strong>File type:</strong> {results.type}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        );
      case 'analyze':
        return (
          <Card>
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" alignItems="center" gap={2}>
                  <CheckCircleIcon color="success" />
                  <Typography variant="h6" color="success.main">
                    {results.extracted_info && results.extracted_info.name
                      ? `Analysing User ${results.extracted_info.name} details:`
                      : 'Analysis Complete'}
                  </Typography>
                </Box>
                {results.extracted_info && (
                  <Box pl={4}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Contact:</strong> {results.extracted_info.contact_no || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Email:</strong> {results.extracted_info.email || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Current Job Title:</strong> {results.extracted_info.current_job_title || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Years of Experience:</strong> {results.extracted_info.years_of_exp || 'N/A'}
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        );
      case 'search':
        return (
          <Box>
            <Typography variant="h6" gutterBottom>Available Jobs</Typography>
            {results.map((job, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6">{job.title}</Typography>
                  <Typography color="textSecondary">{job.company}</Typography>
                  <Typography>{job.location}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        );
      case 'match':
        return (
          <Box>
            <Typography variant="h6" gutterBottom>Job Matches</Typography>
            {results.map((match, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6">{match.job}</Typography>
                  <Typography color="primary">Match: {match.match}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 2, mb: 4 }}>
        <Container>
          <Typography variant="h4" align="center">
            Job Search Platform
          </Typography>
        </Container>
      </Box>

      <Container>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, mb: 4 }}>
              <Grid container spacing={2} justifyContent="center">
                <Grid item>
                  <Button
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                    onClick={() => handleButtonClick('upload')}
                    sx={{ minWidth: 200 }}
                  >
                    Upload Resume
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="contained"
                    startIcon={<AnalyticsIcon />}
                    onClick={() => handleButtonClick('analyze')}
                    sx={{ minWidth: 200 }}
                  >
                    Analyze Resume
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="contained"
                    startIcon={<SearchIcon />}
                    onClick={() => handleButtonClick('search')}
                    sx={{ minWidth: 200 }}
                  >
                    Job Search
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="contained"
                    startIcon={<CompareIcon />}
                    onClick={() => handleButtonClick('match')}
                    sx={{ minWidth: 200 }}
                  >
                    Match Jobs
                  </Button>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                {activeSection ? `${activeSection.charAt(0).toUpperCase() + activeSection.slice(1)} Results` : 'Select an option above'}
              </Typography>
              <Divider sx={{ mb: 3 }} />
              {renderResults()}
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.doc,.docx"
        style={{ display: 'none' }}
      />

      {/* Upload Dialog */}
      <Dialog open={openUploadDialog} onClose={handleCloseDialog}>
        <DialogTitle>Upload Resume</DialogTitle>
        <DialogContent>
          {uploadError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {uploadError}
            </Alert>
          )}
          <List>
            <ListItem button onClick={handleUploadClick}>
              <ListItemIcon>
                <DescriptionIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Select Resume File" 
                secondary="Supported formats: PDF (.pdf), Word (.doc, .docx)"
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default App; 