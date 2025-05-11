import 'styled-components';

declare module 'styled-components' {
  export interface DefaultTheme {
    background: string;
    sidebar: string;
    card: string;
    text: string;
    shadow: string;
    blur: string;
  }
}