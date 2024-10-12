import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_BASE_URL } from '@/config';
import { useToast } from "@/hooks/use-toast";
import { useTheme } from "next-themes";
import { Button } from '@/components/ui/button';

const CALIBRATION_POINTS = [
  { x: 0, y: 0, label: 'Top Left' },
  { x: 0.5, y: 0, label: 'Top Center' },
  { x: 1, y: 0, label: 'Top Right' },
  { x: 0, y: 0.5, label: 'Middle Left' },
  { x: 0.5, y: 0.5, label: 'Center' },
  { x: 1, y: 0.5, label: 'Middle Right' },
  { x: 0, y: 1, label: 'Bottom Left' },
  { x: 0.5, y: 1, label: 'Bottom Center' },
  { x: 1, y: 1, label: 'Bottom Right' },
];

export function Calibration({ onClose }: { onClose: () => void }) {
  const [currentPoint, setCurrentPoint] = useState(0);
  const [calibrationData, setCalibrationData] = useState<[number, number][]>([]);
  const { session } = useAuth();
  const { toast } = useToast();
  const { theme } = useTheme();
  const [calibrationStep, setCalibrationStep] = useState<'browser' | 'recorder' | 'player'>('browser');

  useEffect(() => {
    if (calibrationData.length === CALIBRATION_POINTS.length) {
      handleCalibrationComplete(calibrationData);
    }
  }, [calibrationData]);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    setCalibrationData([...calibrationData, [x, y]]);
    setCurrentPoint(currentPoint + 1);
  };

  const saveCalibrationData = async (data: number[][], type: 'browser' | 'recorder' | 'player') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/calibrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ 
          calibration_data: data, 
          type,
          aspect_ratio: window.innerWidth / window.innerHeight
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save calibration data');
      }
      const responseData = await response.json();
      console.log("Calibration data saved successfully:", responseData);
      toast({
        title: `${type.charAt(0).toUpperCase() + type.slice(1)} Calibration Complete`,
        description: `Your ${type} calibration data has been saved successfully.`,
      });
    } catch (error) {
      console.error(`Error saving ${type} calibration data:`, error);
      toast({
        title: "Calibration Error",
        description: `Failed to save ${type} calibration data: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
      throw error;
    }
  };

  const handleCalibrationComplete = async (calibrationData: number[][]) => {
    try {
      if (calibrationStep === 'browser') {
        await saveCalibrationData(calibrationData, 'browser');
        // Request backend to start recorder calibration
        const response = await fetch(`${API_BASE_URL}/api/start_recorder_calibration`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session?.access_token}`,
          },
        });
        const { url } = await response.json();
        window.open(url, '_blank'); // Open recorder calibration in new window
      } else if (calibrationStep === 'recorder') {
        await saveCalibrationData(calibrationData, 'recorder');
        setCalibrationStep('player');
        setCurrentPoint(0);
        setCalibrationData([]);
        // Request backend to start player calibration
        const playerResponse = await fetch(`${API_BASE_URL}/api/start_player_calibration`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session?.access_token}`,
          },
        });
        if (!playerResponse.ok) {
          throw new Error('Failed to start player calibration');
        }
        toast({
          title: "Player Calibration",
          description: "Please complete the calibration in the player window.",
        });
      } else {
        await saveCalibrationData(calibrationData, 'player');
        toast({
          title: "Calibration Complete",
          description: "All calibration steps have been completed successfully.",
        });
        onClose();
      }
    } catch (error) {
      console.error('Error during calibration:', error);
      toast({
        title: "Calibration Error",
        description: `An error occurred during calibration: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  };

  const isDarkMode = theme === 'dark';

  const handleCancel = () => {
    // You might want to add an API call here to delete any partial calibration data
    onClose();
  };

  if (currentPoint >= CALIBRATION_POINTS.length) {
    return (
      <div className={`flex items-center justify-center h-full ${isDarkMode ? 'text-white' : 'text-black'}`}>
        Calibration step complete! Please wait...
      </div>
    );
  }

  const point = CALIBRATION_POINTS[currentPoint];

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div 
        className={`relative w-[80vw] h-[80vh] ${isDarkMode ? 'bg-gray-800' : 'bg-gray-200'}`}
        onClick={handleClick}
        style={{ cursor: 'crosshair' }}
      >
        {CALIBRATION_POINTS.map((p, index) => (
          <div 
            key={index}
            className={`absolute w-4 h-4 ${
              index === currentPoint ? 'bg-red-500 animate-pulse' : 
              index < currentPoint ? 'bg-green-500' : 
              isDarkMode ? 'bg-blue-400' : 'bg-blue-600'
            }`}
            style={{ 
              left: `${p.x * 100}%`, 
              top: `${p.y * 100}%`,
              transform: 'translate(-50%, -50%)',
            }}
          />
        ))}
        <div className="absolute top-4 left-4 bg-gray-700 text-white p-2 shadow">
          Step {calibrationStep === 'browser' ? '1: Browser' : calibrationStep === 'recorder' ? '2: Recorder' : '3: Player'} Calibration
          <br />
          {currentPoint < CALIBRATION_POINTS.length ? (
            `Click the ${point.label} point (${currentPoint + 1}/${CALIBRATION_POINTS.length})`
          ) : (
            'Calibration complete for this step. Click "Next" to continue.'
          )}
        </div>
        <div className="absolute bottom-4 right-4 flex gap-2">
          <Button onClick={handleCancel} variant="secondary">Cancel</Button>
          {currentPoint >= CALIBRATION_POINTS.length && (
            <Button onClick={() => handleCalibrationComplete(calibrationData)}>
              {calibrationStep === 'player' ? 'Complete' : 'Next Step'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
