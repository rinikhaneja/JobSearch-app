import React, { useState } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const ResumeUpload = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadedFilename, setUploadedFilename] = useState(null);
  const [userId, setUserId] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://localhost:8000/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setUploadedFilename(response.data.filename);
      setUserId(response.data.user_id);
      setSessionId(response.data.session_id);
      sessionStorage.setItem('user_id', response.data.user_id);
      sessionStorage.setItem('session_id', response.data.session_id);
      setUploading(false);
    } catch (error) {
      console.error('Error uploading resume:', error);
      setUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedFilename || !userId || !sessionId) return;

    setAnalyzing(true);
    try {
      const userId = sessionStorage.getItem('user_id');
      const sessionId = sessionStorage.getItem('session_id');
      console.log(userId, sessionId);
      const response = await axios.post('http://localhost:8000/analyze-resume', {
        user_id: userId,
        session_id: sessionId
      });
      onUploadSuccess(response.data);
      setAnalyzing(false);
    } catch (error) {
      console.error('Error analyzing resume:', error);
      setAnalyzing(false);
    }
  };

  return (
    <Box sx={{ textAlign: 'center', p: 3 }}>
      <input
        accept=".pdf,.doc,.docx"
        style={{ display: 'none' }}
        id="resume-file"
        type="file"
        onChange={handleFileSelect}
      />
      <label htmlFor="resume-file">
        <Button
          variant="contained"
          component="span"
          startIcon={<CloudUploadIcon />}
          disabled={uploading || analyzing}
        >
          Select Resume
        </Button>
      </label>
      
      {selectedFile && (
        <Typography variant="body2" sx={{ mt: 2 }}>
          Selected file: {selectedFile.name}
        </Typography>
      )}

      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!selectedFile || uploading || analyzing}
          sx={{ mr: 2 }}
        >
          {uploading ? <CircularProgress size={24} /> : 'Upload Resume'}
        </Button>

        <Button
          variant="contained"
          onClick={handleAnalyze}
          disabled={!uploadedFilename || analyzing}
          color="secondary"
        >
          {analyzing ? <CircularProgress size={24} /> : 'Analyze Resume'}
        </Button>
      </Box>
    </Box>
  );
};

export default ResumeUpload; 