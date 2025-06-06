import React, { useState, useRef } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
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
import { ERROR_MESSAGES, SUCCESS_MESSAGES, UPLOAD_LABEL, ANALYZE_LABEL, JOB_SEARCH_LABEL, MATCH_JOBS_LABEL, SUPPORTED_FORMATS } from './constants/messages';
import ResumeAnalysis from './components/ResumeAnalysis';
import ResultsCard from './components/ResultsCard';
import JobSearch from './components/JobSearch';
import JobMatch from './components/JobMatch';
import Grid from '@mui/material/Grid';
import ResumeUpload from './components/ResumeUpload';
import {
  ApiError,
  UploadResponse,
  AnalysisResponse,
  Job,
  Match,
  UploadResults,
  Results
} from './types/jobsearch';

const LOG_LEVEL = (process.env.LOG_LEVEL || process.env.REACT_APP_LOG_LEVEL || 'INFO').toUpperCase();
const isDebug = LOG_LEVEL === 'DEBUG';

/**
 * Main application component for the Job Search Platform.
 * Handles navigation, state, and rendering of all major UI sections (upload, analysis, job search, match).
 */
const App: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [openUploadDialog, setOpenUploadDialog] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  if (LOG_LEVEL === 'DEBUG') {
    console.info('App component mounted [DEBUG MODE]');
  } else {
    console.info('App component mounted');
  }

  const handleButtonClick = (section: string) => {
    if (section === 'upload') {
      setUserId(null);
      setSessionId(null);
      setOpenUploadDialog(true);
      isDebug && console.debug('Open upload dialog set to true');
      return;
    }
    setActiveSection(section);
    isDebug && console.debug('Active section set to:', section);
  };

  const handleUploadSuccess = (file: File, uploadResult: any) => {
    setResults({
      message: SUCCESS_MESSAGES.UPLOAD_SUCCESS(file.name),
      path: uploadResult.location,
      size: `${(file.size / 1024).toFixed(2)} KB`,
      type: file.type,
      user_id: uploadResult.user_id,
      session_id: uploadResult.session_id
    });
    setUserId(uploadResult.user_id);
    setSessionId(uploadResult.session_id);
    setActiveSection('upload');
    setUploadError(null);
    setOpenUploadDialog(false);
    if (isDebug) console.debug('Upload success:', uploadResult);
  };

  const handleAnalyzeSuccess = (analysisResult: any) => {
    setResults({
      message: analysisResult.message,
      extracted_info: analysisResult.extracted_info
    });
    setActiveSection('analyze');
    setUploadError(null);
    setOpenUploadDialog(false);
    if (isDebug) console.debug('Analyze success:', analysisResult);
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
          <>
            <ResultsCard results={results as UploadResults} />
            {userId && sessionId && (
              <ResumeAnalysis userId={userId} sessionId={sessionId} onAnalyzeSuccess={handleAnalyzeSuccess} />
            )}
          </>
        );
      case 'analyze':
        return <ResultsCard results={results as { message: string; extracted_info: AnalysisResponse['extracted_info'] }} />;
      case 'search':
        if (!userId || !sessionId) {
          return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
              <Typography variant="h6" color="textSecondary">
                Please upload your resume first
              </Typography>
            </Box>
          );
        }
        return <JobSearch 
          jobs={results as Job[]} 
          user_id={userId} 
          session_id={sessionId} 
        />;
      case 'match':
        return <JobMatch matches={results as Match[]} />;
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
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Paper sx={{ p: 3, mb: 4, width: '100%' }}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                startIcon={<CloudUploadIcon />}
                onClick={() => handleButtonClick('upload')}
                sx={{ minWidth: 200 }}
              >
                {UPLOAD_LABEL}
              </Button>
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={() => handleButtonClick('search')}
                sx={{ minWidth: 200 }}
              >
                {JOB_SEARCH_LABEL}
              </Button>
              <Button
                variant="contained"
                startIcon={<CompareIcon />}
                onClick={() => handleButtonClick('match')}
                sx={{ minWidth: 200 }}
              >
                {MATCH_JOBS_LABEL}
              </Button>
            </Box>
          </Paper>

          {renderResults()}

          <Dialog open={openUploadDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
            <DialogTitle>Upload Resume</DialogTitle>
            <DialogContent>
              <ResumeUpload onUploadSuccess={handleUploadSuccess} />
            </DialogContent>
          </Dialog>
        </Box>
      </Container>
    </div>
  );
};

export default App; 