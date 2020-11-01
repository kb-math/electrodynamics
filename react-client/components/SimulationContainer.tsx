import React, { useRef } from 'react';
import { View } from 'react-native';

export function SimulationContainer(): React.ReactElement {
  const ref = useRef(null);
  return <View ref={ref} />;
}
