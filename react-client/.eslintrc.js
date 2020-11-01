module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  extends: ['@react-native-community', 'eslint:recommended', 'plugin:react/recommended'],
  plugins: ['react', '@typescript-eslint', 'react-hooks'],
  rules: {
    'comma-dangle': ['error', 'never'],
    'quote-props': ['error', 'as-needed'],
    'max-len': ['error', { code: 120 }],
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn'
  }
};
