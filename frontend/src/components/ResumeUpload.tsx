import React, { useState, useRef } from 'react';
import { Box, Button, Typography, CircularProgress, Alert, Paper, Fade, FormControlLabel, Switch } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { ERROR_MESSAGES } from '../constants/messages';

interface ResumeUploadProps {
  onUploadSuccess: (file: File, uploadResult: any) => void;
}

/**
 * Component for uploading a resume file.
 * Handles file selection, upload, and triggers callback on success.
 * Enhanced with modern, visually appealing UI.
 */
const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [useLLM, setUseLLM] = useState<boolean>(true);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setSuccess(false);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setSuccess(false);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError(ERROR_MESSAGES.UPLOAD_ERROR);
      return;
    }
    setUploading(true);
    setError(null);
    setSuccess(false);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('use_llm', useLLM.toString());
      const response = await fetch('http://localhost:8000/upload-resume', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || ERROR_MESSAGES.UPLOAD_ERROR);
      }
      const data = await response.json();
      setUploadResult(data);
      onUploadSuccess(selectedFile, data);
      setSelectedFile(null);
      setSuccess(true);
    } catch (error) {
      setError(error instanceof Error ? error.message : ERROR_MESSAGES.UPLOAD_ERROR);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Fade in timeout={500}>
      <Paper elevation={4} sx={{ maxWidth: 1200, mx: 'auto', p: 4, borderRadius: 3, boxShadow: 6 }}>
        <Box sx={{ mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={useLLM}
                onChange={(e) => setUseLLM(e.target.checked)}
                color="primary"
              />
            }
            label="Use AI-Powered Resume Parser"
          />
          <Typography variant="caption" color="text.secondary" display="block">
            {useLLM ? "Using OpenAI GPT for parsing" : "Using traditional parser"}
          </Typography>
        </Box>
        <Box
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          sx={{
            border: '2px dashed',
            borderColor: selectedFile ? 'success.main' : 'primary.light',
            borderRadius: 2,
            p: 3,
            textAlign: 'center',
            bgcolor: selectedFile ? 'success.lighter' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.2s',
            mb: 2,
            position: 'relative',
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            accept=".pdf,.doc,.docx"
            style={{ display: 'none' }}
            id="resume-upload"
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
          />
          {success ? (
            <>
              <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 1 }} />
              <Typography variant="h6" color="success.main">Upload Successful!</Typography>
            </>
          ) : (
            <>
              <CloudUploadIcon color={selectedFile ? 'success' : 'primary'} sx={{ fontSize: 48, mb: 1 }} />
              <Typography variant="h6" color={selectedFile ? 'success.main' : 'primary.main'}>
                {selectedFile ? 'Ready to Upload' : 'Drag & Drop or Click to Select File'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Supported formats: PDF (.pdf), Word (.doc, .docx)
              </Typography>
            </>
          )}
          {selectedFile && !success && (
            <Typography variant="body2" sx={{ mt: 2 }}>
              Selected file: <b>{selectedFile.name}</b>
            </Typography>
          )}
        </Box>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Button
          variant="contained"
          color={success ? 'success' : 'primary'}
          onClick={handleUpload}
          disabled={!selectedFile || uploading || success}
          fullWidth
          size="large"
          sx={{ mt: 1, fontWeight: 600, letterSpacing: 1 }}
          startIcon={uploading ? <CircularProgress size={22} color="inherit" /> : <CloudUploadIcon />}
        >
          {uploading ? 'Uploading...' : success ? 'Uploaded' : 'Upload'}
        </Button>
      </Paper>
    </Fade>
  );
};

export default ResumeUpload; 