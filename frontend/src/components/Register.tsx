import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Button, Input, VStack, Text, useToast, Box, Heading } from '@chakra-ui/react';
import axios from 'axios';

const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const router = useRouter();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/api/register', {
        username,
        password,
        email,
      });
      toast({
        title: 'Registration successful',
        description: 'You can now log in with your new account',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      router.push('/login');
    } catch (error) {
      toast({
        title: 'Registration failed',
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
        Create your account
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
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
            Register
          </Button>
        </VStack>
      </form>
      <Text mt={4} textAlign="center" color="white">
        Already have an account? <Button variant="link" color="purple.300" onClick={() => router.push('/login')}>Log in</Button>
      </Text>
    </Box>
  );
};

export default Register;