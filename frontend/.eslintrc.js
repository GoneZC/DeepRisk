module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2021: true
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  parser: 'vue-eslint-parser', // 必须指定Vue解析器
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    parser: '@babel/eslint-parser',
    requireConfigFile: false // 禁用Babel配置文件检查
  },
  plugins: ['vue'],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-unused-vars': 'off',
    'vue/multi-word-component-names': 'off'
  }
} 