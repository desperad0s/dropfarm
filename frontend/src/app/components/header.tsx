import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../../contexts/AuthContext';
import { Button, Flex, Box, useColorMode, IconButton } from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';

const Header: React.FC = () => {
  const { isAuthenticated, logout, checkAuth } = useAuth();
  const router = useRouter();
  const { colorMode, toggleColorMode } = useColorMode();

  useEffect(() => {
    checkAuth();
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <Flex as="nav" align="center" justify="space-between" wrap="wrap" padding="1.5rem" bg="gray.800" color="white">
      <Flex align="center" mr={5}>
        <Box as="span" fontWeight="bold" fontSize="xl">
          Dropfarm
        </Box>
      </Flex>

      <Flex align="center">
        {isAuthenticated ? (
          <>
            <Link href="/dashboard" passHref>
              <Button as="a" variant="ghost" mr={3}>
                Dashboard
              </Button>
            </Link>
            <Link href="/projects" passHref>
              <Button as="a" variant="ghost" mr={3}>
                Projects
              </Button>
            </Link>
            <Link href="/settings" passHref>
              <Button as="a" variant="ghost" mr={3}>
                Settings
              </Button>
            </Link>
            <Button onClick={handleLogout} colorScheme="red">
              Logout
            </Button>
          </>
        ) : (
          <Link href="/login" passHref>
            <Button as="a" colorScheme="blue">
              Login
            </Button>
          </Link>
        )}
        <IconButton
          aria-label="Toggle color mode"
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          ml={3}
        />
      </Flex>
    </Flex>
  );
};

export default Header;