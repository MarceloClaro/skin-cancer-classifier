import { useSyncExternalStore } from 'react';

/**
 * Hook que retorna true apenas no cliente (não no servidor).
 * Usa useSyncExternalStore para evitar erros de hidratação.
 * 
 * Baseado em: https://tkdodo.eu/blog/avoiding-hydration-mismatches-with-use-sync-external-store
 */
export function useIsClient() {
  return useSyncExternalStore(
    () => () => {}, // subscribe: função vazia (não há mudanças)
    () => true,      // getSnapshot: sempre true no cliente
    () => false      // getServerSnapshot: sempre false no servidor
  );
}
