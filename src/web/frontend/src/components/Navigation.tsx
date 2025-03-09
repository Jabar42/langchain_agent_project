import React from 'react';
import {
  Box,
  Flex,
  HStack,
  Link,
  IconButton,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  useColorModeValue,
  Stack,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon } from '@chakra-ui/icons';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface NavLinkProps {
  children: React.ReactNode;
  to: string;
}

const NavLink = ({ children, to }: NavLinkProps) => (
  <Link
    as={RouterLink}
    px={2}
    py={1}
    rounded={'md'}
    _hover={{
      textDecoration: 'none',
      bg: useColorModeValue('gray.200', 'gray.700'),
    }}
    to={to}
  >
    {children}
  </Link>
);

export const Navigation = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isAuthenticated, logout } = useAuth();

  const Links = [
    { name: 'Dashboard', path: '/' },
    { name: 'Chat', path: '/chat' },
    { name: 'Comparar Modelos', path: '/compare' },
  ];

  return (
    <Box bg={useColorModeValue('gray.100', 'gray.900')} px={4} width="100%">
      <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
        <IconButton
          size={'md'}
          icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
          aria-label={'Open Menu'}
          display={{ md: 'none' }}
          onClick={isOpen ? onClose : onOpen}
        />
        <HStack spacing={8} alignItems={'center'}>
          <Box fontWeight="bold">AI Agent Platform</Box>
          <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
            {isAuthenticated &&
              Links.map((link) => (
                <NavLink key={link.path} to={link.path}>
                  {link.name}
                </NavLink>
              ))}
          </HStack>
        </HStack>
        <Flex alignItems={'center'}>
          {isAuthenticated ? (
            <Button
              variant={'solid'}
              colorScheme={'blue'}
              size={'sm'}
              mr={4}
              onClick={logout}
            >
              Cerrar Sesión
            </Button>
          ) : (
            <Button
              as={RouterLink}
              to="/login"
              variant={'solid'}
              colorScheme={'blue'}
              size={'sm'}
              mr={4}
            >
              Iniciar Sesión
            </Button>
          )}
        </Flex>
      </Flex>

      {isOpen ? (
        <Box pb={4} display={{ md: 'none' }}>
          <Stack as={'nav'} spacing={4}>
            {isAuthenticated &&
              Links.map((link) => (
                <NavLink key={link.path} to={link.path}>
                  {link.name}
                </NavLink>
              ))}
          </Stack>
        </Box>
      ) : null}
    </Box>
  );
}; 