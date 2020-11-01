import React, { useEffect, useRef } from 'react';
import { View } from 'react-native';
import { initClient } from './init';

export function SimulationContainer(): React.ReactElement {
  const ref = useRef(null);
  useEffect(() => {
    initClient();
  });
  return <View ref={ref} />;
}
