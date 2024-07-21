import React, { useState } from 'react';
import { Container, TextField, Button, Box, Typography, Paper, IconButton, CircularProgress } from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import axios from 'axios';

function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [fileName, setFileName] = useState('');
  const [uploadMessage, setUploadMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:8000/query', { params: { question: query } });
      setResponse(res.data.answer);
    } catch (error) {
      console.error(error);
      setResponse('Error submitting query.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setFileName(file.name);
      const formData = new FormData();
      formData.append('file', file);
      setLoading(true);
      try {
        const res = await axios.post('http://localhost:8000/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setUploadMessage(res.data.message);
      } catch (error) {
        console.error(error);
        setUploadMessage('Error uploading file.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Container maxWidth="md" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Box my={4} style={{ flex: 1 }}>
        <Typography variant="h3" component="h1" gutterBottom style={{ fontWeight: 'bold', textAlign: 'center', color: 'black' }}>
          Chatbot
        </Typography>
        {uploadMessage && (
          <Paper elevation={3} style={{ padding: '16px', marginBottom: '16px', borderRadius: '20px', borderColor: 'lightgrey', borderStyle: 'solid' }}>
            <Typography variant="h6" style={{ color: 'black' }}>Upload Status:</Typography>
            <Typography>{uploadMessage}</Typography>
          </Paper>
        )}
        {response && (
          <Paper elevation={3} style={{ padding: '16px', marginBottom: '16px', borderRadius: '20px', borderColor: 'lightgrey', borderStyle: 'solid' }}>
            <Typography variant="h6" style={{ color: 'black' }}>Response:</Typography>
            <Typography>{response}</Typography>
          </Paper>
        )}
      </Box>
      <Paper elevation={3} style={{ padding: '16px', borderRadius: '20px', borderColor: 'lightgrey', borderStyle: 'solid', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {fileName && (
          <Typography variant="body2" color="textSecondary" style={{ marginBottom: '8px', color: 'black' }}>
            Uploaded file: {fileName}
          </Typography>
        )}
        <input
          accept="application/pdf"
          style={{ display: 'none' }}
          id="icon-button-file"
          type="file"
          onChange={handleFileUpload}
        />
        <label htmlFor="icon-button-file">
          <IconButton color="primary" component="span">
            <CloudUploadIcon style={{ color: 'black' }} />
          </IconButton>
        </label>
        <TextField
          label="Ask me anything"
          fullWidth
          variant="outlined"
          multiline
          minRows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ marginTop: '16px' }}
        />
        <Button variant="contained" onClick={handleSubmit} style={{ backgroundColor: 'black', color: 'white', marginTop: '16px' }}>
          Submit
        </Button>
        {loading && <CircularProgress style={{ marginTop: '16px' }} />}
      </Paper>
    </Container>
  );
}

export default Home;
