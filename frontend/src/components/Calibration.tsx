import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_BASE_URL } from '@/config';
import { useToast } from "@/hooks/use-toast";
import { useTheme } from "next-themes";

const CALIBRATION_POINTS = [
  { x: 0, y: 0, label: 'Top Left' },
  { x: 320, y: 0, label: 'Top Left-Center' },
  { x: 640, y: 0, label: 'Top Center' },
  { x: 960, y: 0, label: 'Top Right-Center' },
  { x: 1280, y: 0, label: 'Top Right' },
  { x: 0, y: 180, label: 'Left Upper-Middle' },
  { x: 320, y: 180, label: 'Left-Center Upper-Middle' },
  { x: 640, y: 180, label: 'Center Upper-Middle' },
  { x: 960, y: 180, label: 'Right-Center Upper-Middle' },
  { x: 1280, y: 180, label: 'Right Upper-Middle' },
  { x: 0, y: 360, label: 'Middle Left' },
  { x: 320, y: 360, label: 'Middle Left-Center' },
  { x: 640, y: 360, label: 'Center' },
  { x: 960, y: 360, label: 'Middle Right-Center' },
  { x: 1280, y: 360, label: 'Middle Right' },
  { x: 0, y: 540, label: 'Left Lower-Middle' },
  { x: 320, y: 540, label: 'Left-Center Lower-Middle' },
  { x: 640, y: 540, label: 'Center Lower-Middle' },
  { x: 960, y: 540, label: 'Right-Center Lower-Middle' },
  { x: 1280, y: 540, label: 'Right Lower-Middle' },
  { x: 0, y: 720, label: 'Bottom Left' },
  { x: 320, y: 720, label: 'Bottom Left-Center' },
  { x: 640, y: 720, label: 'Bottom Center' },
  { x: 960, y: 720, label: 'Bottom Right-Center' },
  { x: 1280, y: 720, label: 'Bottom Right' },
];

export function Calibration({ onClose }: { onClose: () => void }) {
  const [currentPoint, setCurrentPoint] = useState(0);
  const [calibrationData, setCalibrationData] = useState<[number, number][]>([]);
  const { session } = useAuth();
  const { toast } = useToast();
  const { theme } = useTheme();

  useEffect(() => {
    if (calibrationData.length === CALIBRATION_POINTS.length) {
      saveCalibrationData();
    }
  }, [calibrationData]);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);
    setCalibrationData([...calibrationData, [x, y]]);
    setCurrentPoint(currentPoint + 1);
  };

  const saveCalibrationData = async () => {
    try {
      console.log("Attempting to save calibration data:", calibrationData);
      console.log("Session token:", session?.access_token);
      const response = await fetch(`${API_BASE_URL}/api/calibrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ calibration_data: calibrationData }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error response:", errorData);
        throw new Error(errorData.error || 'Failed to save calibration data');
      }
      const data = await response.json();
      console.log("Calibration data saved successfully:", data);
      toast({
        title: "Calibration Complete",
        description: "Your calibration data has been saved successfully.",
      });
      setTimeout(onClose, 2000);  // Close the calibration modal after 2 seconds
    } catch (error) {
      console.error('Error saving calibration data:', error);
      toast({
        title: "Calibration Error",
        description: `Failed to save calibration data: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  };

  const isDarkMode = theme === 'dark';

  if (currentPoint >= CALIBRATION_POINTS.length) {
    return (
      <div className={`flex items-center justify-center h-full ${isDarkMode ? 'text-white' : 'text-black'}`}>
        Calibration complete!
      </div>
    );
  }

  const point = CALIBRATION_POINTS[currentPoint];

  return (
    <div 
      className={`relative w-[1280px] h-[720px] ${isDarkMode ? 'bg-gray-800' : 'bg-gray-200'}`}
      onClick={handleClick}
      style={{ cursor: 'crosshair' }}
    >
      {CALIBRATION_POINTS.map((p, index) => (
        <div 
          key={index}
          className={`absolute w-4 h-4 rounded-full ${index === currentPoint ? 'bg-red-500' : (isDarkMode ? 'bg-blue-400' : 'bg-blue-600')}`}
          style={{ 
            left: `${(p.x / 1280) * 100}%`, 
            top: `${(p.y / 720) * 100}%`,
            transform: 'translate(-50%, -50%)',
            border: '2px solid white',
            boxShadow: '0 0 0 1px black'
          }}
        />
      ))}
      <div 
        className={`absolute top-4 left-4 ${isDarkMode ? 'bg-gray-700 text-white' : 'bg-white text-black'} p-2 rounded shadow`}
        style={{ zIndex: 10 }}
      >
        Click the {point.label} point
      </div>
    </div>
  );
}
