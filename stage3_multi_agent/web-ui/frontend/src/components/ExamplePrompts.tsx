import React from 'react';
import {
  Box,
  Typography,
  Button,
  Stack,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

interface ExamplePromptsProps {
  selectedAgent: string;
  onSelectPrompt: (prompt: string) => void;
}

const EXAMPLE_PROMPTS: Record<string, string[]> = {
  'product-catalog': [
    'Show me all laptops',
    'Find laptops that are in stock and analyze their sales performance',
    'Which TechCorp products are bestsellers?',
    'Show me products under $500 that need restocking',
    'Find all SmartLife products and check their inventory levels',
  ],
  'inventory-management': [
    'Check stock levels for all laptops and their recent sales',
    'Which bestselling products are running low on stock?',
    'Find products with high sales velocity that need restocking',
    'What products have low inventory but high customer demand?',
    'Analyze inventory turnover for top-selling categories',
  ],
  'sales-analytics': [
    'What are the top 5 selling products and their current stock levels?',
    'Which products have high sales but low inventory?',
    'Analyze sales performance for products that are out of stock',
    'Find underperforming products with excess inventory',
    'Which product categories need inventory optimization based on sales trends?',
  ],
};

const ExamplePrompts: React.FC<ExamplePromptsProps> = ({
  selectedAgent,
  onSelectPrompt,
}) => {
  const prompts = EXAMPLE_PROMPTS[selectedAgent] || [];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Example Prompts
      </Typography>
      
      <Stack spacing={1}>
        {prompts.map((prompt, index) => (
          <Button
            key={index}
            variant="outlined"
            size="small"
            startIcon={<PlayArrowIcon />}
            onClick={() => onSelectPrompt(prompt)}
            sx={{
              justifyContent: 'flex-start',
              textAlign: 'left',
              textTransform: 'none',
              fontSize: '0.875rem',
            }}
          >
            {prompt}
          </Button>
        ))}
      </Stack>

      {prompts.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          No example prompts available for this agent
        </Typography>
      )}
    </Box>
  );
};

export default ExamplePrompts;