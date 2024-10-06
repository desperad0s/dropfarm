'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const { access_token } = await response.json();
      localStorage.setItem('token', access_token);
      router.push('/');
    } else {
      alert('Login failed');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <form onSubmit={handleSubmit} className="max-w-sm mx-auto">
        <Input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="mb-2"
        />
        <Input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="mb-2"
        />
        <Button type="submit">Login</Button>
      </form>
    </div>
  );
}