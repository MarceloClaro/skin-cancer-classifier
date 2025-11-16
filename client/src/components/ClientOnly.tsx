import { useEffect, useState } from 'react';

/**
 * Componente que renderiza children apenas no cliente (não no SSR).
 * Evita erros de hidratação com componentes que usam Portals.
 */
export function ClientOnly({ children }: { children: React.ReactNode }) {
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) {
    return null;
  }

  return <>{children}</>;
}
