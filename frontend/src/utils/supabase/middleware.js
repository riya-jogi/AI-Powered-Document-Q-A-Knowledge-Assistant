import { createClient } from './client';

export const initializeSession = () => {
  const supabase = createClient();

  const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
    if (session && (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED')) {
      localStorage.setItem('supabase_session', JSON.stringify(session));
    }

    if (event === 'SIGNED_OUT') {
      localStorage.removeItem('supabase_session');
    }
  });

  return { supabase, authListener };
};

export default initializeSession;
