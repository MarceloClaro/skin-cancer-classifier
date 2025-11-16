# Pesquisa sobre Erro de Hidratação React

## Problema
```
NotFoundError: Falha ao executar 'insertBefore' em 'Node': O nó antes do qual o novo nó deve ser inserido não é filho deste nó.
```

## Causas Comuns (baseado em documentação oficial)

### 1. **Mismatch entre Server e Client**
- O HTML renderizado no servidor difere do HTML gerado no cliente
- React espera que o primeiro render no cliente seja idêntico ao do servidor

### 2. **Uso de APIs do Browser**
- `window`, `document`, `localStorage` usados antes da montagem
- Valores que só existem no cliente (não no servidor)

### 3. **Renderização Condicional Problemática**
- Condições baseadas em estado que muda entre server e client
- Timestamps, random numbers, IDs gerados dinamicamente

### 4. **Componentes de Terceiros**
- Extensões de browser injetando HTML (ex: Colorzilla)
- Scripts externos modificando DOM

## Soluções Documentadas

### Solução 1: `suppressHydrationWarning`
```tsx
<div suppressHydrationWarning>
  {/* Conteúdo que pode ter mismatch */}
</div>
```
**Quando usar:** Quando o mismatch é intencional e conhecido
**Limitação:** Não resolve o problema, apenas suprime o warning

### Solução 2: Client-Only Rendering
```tsx
const [isClient, setIsClient] = useState(false);

useEffect(() => {
  setIsClient(true);
}, []);

if (!isClient) return null; // ou skeleton
```
**Quando usar:** Componentes que dependem de APIs do browser
**Problema:** Causa flash de conteúdo (FOUC)

### Solução 3: `useSyncExternalStore` (React 18+)
```tsx
import { useSyncExternalStore } from 'react';

const subscribe = () => () => {};
const getSnapshot = () => true;
const getServerSnapshot = () => false;

const isClient = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
```
**Quando usar:** Para sincronizar estado entre server e client
**Vantagem:** Não causa FOUC

### Solução 4: Dynamic Import com `ssr: false` (Next.js)
```tsx
const ClientComponent = dynamic(() => import('./ClientComponent'), {
  ssr: false
});
```
**Quando usar:** Componentes puramente client-side
**Limitação:** Específico do Next.js

## Nossa Situação

### Template Atual
- **Framework:** Vite + React 19 + Wouter
- **SSR:** Não configurado explicitamente (CSR puro)
- **Problema:** Erro ocorre mesmo sem SSR ativo

### Hipótese
O erro pode estar relacionado a:
1. **Hot Module Replacement (HMR)** do Vite causando mismatch
2. **Componentes shadcn/ui (Radix UI)** com portals/teleports
3. **Wouter** tentando manipular DOM antes da montagem completa
4. **React 19** com novo comportamento de hidratação

## Próximos Passos

1. Verificar se o template está realmente usando CSR puro ou se há SSR oculto
2. Investigar componentes shadcn/ui que usam portals (Dialog, Popover, etc.)
3. Testar com `suppressHydrationWarning` em componentes problemáticos
4. Considerar migrar para `useSyncExternalStore` se necessário
5. Verificar configuração do Vite para SSR/hidratação

## Referências
- https://react.dev/reference/react-dom/client/hydrateRoot
- https://medium.com/@praveenb0927/reacts-suppresshydrationwarning-fixing-hydration-errors-causes-solutions-and-best-practices-62977194e6f4
- https://tkdodo.eu/blog/avoiding-hydration-mismatches-with-use-sync-external-store
- https://github.com/facebook/react/issues/13278
