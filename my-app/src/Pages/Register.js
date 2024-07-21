import React from 'react';
import { TextField, Button, Grid, Container, Typography, InputAdornment } from '@mui/material';
import { AccountCircle, Email, Phone, Home, Work } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export default function Register() {
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    const formEle = document.querySelector('form');
    const formData = new FormData(formEle);
    
    fetch(
      'https://script.google.com/macros/s/AKfycbxNfTcJWhdwPTP3DVejo30stWiBXjyHwqhCJUJ6HwZD8Owr4vp3vRgoakcbXNvoB1Vi/exec',
      {
        method: 'POST',
        body: formData,
        mode: 'no-cors'
      }
    )
      .then((res) => {
        console.log(res);
        navigate('/home');
        
      })
      
      .catch((error) => {
        console.error('There has been a problem with your fetch operation:', error);
      });
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Register
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              name="Name"
              label="Name"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AccountCircle />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              name="Email"
              label="Email"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              name="Mobile_No"
              label="Mobile No"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Phone />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              name="Address"
              label="Address"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Home />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              name="Occupation"
              label="Occupation"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Work />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12}>
            <Button type="submit" variant="contained" color="primary">
              Register
            </Button>
          </Grid>
        </Grid>
      </form>
    </Container>
  );
}
