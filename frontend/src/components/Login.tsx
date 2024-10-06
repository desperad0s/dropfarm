import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button, Input, VStack, Text, useToast, Box, Heading } from '@chakra-ui/react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: 'Login failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box maxWidth="400px" margin="auto" mt={8} p={6} borderRadius="md" bg="black">
      <Heading as="h1" size="xl" textAlign="center" mb={6} color="white">
        Sign in to your account
      </Heading>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4}>
          <Input
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            bg="gray.800"
            color="white"
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            bg="gray.800"
            color="white"
          />
          <Button type="submit" colorScheme="purple" width="100%">
            Sign in
          </Button>
        </VStack>
      </form>
      <Text mt={4} textAlign="center" color="white">
        Don't have an account? <Button variant="link" color="purple.300" onClick={() => navigate('/register')}>Create new account</Button>
      </Text>
    </Box>
  );
};

export default Login;