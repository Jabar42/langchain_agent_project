import React, { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  useToast,
  Container,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  CheckboxGroup,
  Checkbox,
  HStack,
} from '@chakra-ui/react';
import { useQuery } from 'react-query';

interface ModelResponse {
  text: string;
  model: string;
  confidence: number;
  metrics: {
    accuracy: number;
    coherence: number;
    relevance: number;
  };
}

interface ComparisonResult {
  responses: { [key: string]: ModelResponse };
  best_model: string;
  comparison: {
    metrics: {
      [key: string]: {
        accuracy: number;
        coherence: number;
        relevance: number;
      };
    };
  };
}

export const ModelComparison: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  // Obtener lista de modelos disponibles
  const { data: models } = useQuery('models', async () => {
    const response = await fetch('http://localhost:8000/models', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) throw new Error('Failed to fetch models');
    return response.json();
  });

  const handleCompare = async () => {
    if (!prompt.trim() || selectedModels.length === 0) {
      toast({
        title: 'Error',
        description: 'Por favor ingresa un prompt y selecciona al menos un modelo',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          text: prompt,
          models: selectedModels,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to compare models');
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo realizar la comparación',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.xl">
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Comparación de Modelos</Heading>
        
        <Box>
          <Text mb={2}>Selecciona los modelos a comparar:</Text>
          <CheckboxGroup
            colorScheme="blue"
            value={selectedModels}
            onChange={(values) => setSelectedModels(values as string[])}
          >
            <HStack spacing={4} wrap="wrap">
              {models?.models?.map((model: string) => (
                <Checkbox key={model} value={model}>
                  {model}
                </Checkbox>
              ))}
            </HStack>
          </CheckboxGroup>
        </Box>

        <Box>
          <Text mb={2}>Prompt:</Text>
          <Input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ingresa el prompt para comparar los modelos..."
          />
        </Box>

        <Button
          colorScheme="blue"
          onClick={handleCompare}
          isLoading={isLoading}
          loadingText="Comparando..."
        >
          Comparar Modelos
        </Button>

        {result && (
          <Box>
            <Heading size="md" mb={4}>
              Resultados de la Comparación
            </Heading>
            
            <Badge colorScheme="green" mb={4}>
              Mejor modelo: {result.best_model}
            </Badge>

            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Modelo</Th>
                  <Th>Respuesta</Th>
                  <Th isNumeric>Precisión</Th>
                  <Th isNumeric>Coherencia</Th>
                  <Th isNumeric>Relevancia</Th>
                </Tr>
              </Thead>
              <Tbody>
                {Object.entries(result.responses).map(([model, response]) => (
                  <Tr key={model}>
                    <Td>
                      <Text fontWeight={model === result.best_model ? 'bold' : 'normal'}>
                        {model}
                      </Text>
                    </Td>
                    <Td maxW="300px" isTruncated>
                      {response.text}
                    </Td>
                    <Td isNumeric>{(response.metrics.accuracy * 100).toFixed(1)}%</Td>
                    <Td isNumeric>{(response.metrics.coherence * 100).toFixed(1)}%</Td>
                    <Td isNumeric>{(response.metrics.relevance * 100).toFixed(1)}%</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        )}
      </VStack>
    </Container>
  );
}; 