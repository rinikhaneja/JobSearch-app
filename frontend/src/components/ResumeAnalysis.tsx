import React, { useState } from 'react';
import { Box, Button, Typography, CircularProgress, Alert } from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import { ERROR_MESSAGES } from '../constants/messages';

interface ResumeAnalysisProps {
  userId: string;
  sessionId: string;
  onAnalyzeSuccess: (analysisResult: any) => void;
}

const ResumeAnalysis: React.FC<ResumeAnalysisProps> = ({ userId, sessionId, onAnalyzeSuccess }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/analyze-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, session_id: sessionId })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || ERROR_MESSAGES.ANALYSIS_ERROR || 'Failed to analyze resume');
      }
      const data = await response.json();
      onAnalyzeSuccess(data);
    } catch (error) {
      let message = 'Error analyzing resume';
      if (typeof error === 'object' && error !== null) {
        if ('response' in error && typeof (error as any).response === 'object' && (error as any).response !== null && 'data' in (error as any).response) {
          message = (error as any).response.data?.detail || message;
        } else if ('detail' in error) {
          message = (error as any).detail || message;
        } else if ('message' in error) {
          message = (error as any).message || message;
        }
      }
      setError(message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <Box sx={{ textAlign: 'center', p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Button
        variant="contained"
        startIcon={<AnalyticsIcon />}
        onClick={handleAnalyze}
        disabled={analyzing}
      >
        {analyzing ? <CircularProgress size={24} /> : 'Analyze Resume'}
      </Button>
    </Box>
  );
};

export default ResumeAnalysis; 