import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

interface Match {
  job: string;
  match: string;
}

interface JobMatchProps {
  matches: Match[];
}

/**
 * Displays a list of matched jobs with their match percentage or score.
 * Expects a matches prop which is an array of match objects.
 */
const JobMatch: React.FC<JobMatchProps> = ({ matches }) => {
  console.info('JobMatch component rendered with matches:', matches);
  return (
    <Box>
      <Typography variant="h6" gutterBottom>Job Matches</Typography>
      {matches.map((match, index) => {
        console.debug('Rendering match:', match);
        return (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6">{match.job}</Typography>
              <Typography variant="body2" color="textSecondary">Match: {match.match}</Typography>
            </CardContent>
          </Card>
        );
      })}
    </Box>
  );
};

export default JobMatch; 