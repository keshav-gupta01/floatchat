import React, { useState } from 'react';

interface SignupFormProps {
  onToggleMode: () => void;
  onSignedIn?: () => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onToggleMode, onSignedIn }) => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setMessage(null);
    setError(null);

    if (!identifier || !password) {
      setError('Please fill in all fields.');
      return;
    }

    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      setMessage('Signed in successfully.');
      if (onSignedIn) onSignedIn();
    } catch (err) {
      setError('Sign in failed. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2 className="auth-title">Welcome back</h2>
        <p className="auth-subtitle">Sign in to your account to continue</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="identifier" className="label">Email or Username</label>
            <input
              id="identifier"
              className="input"
              type="text"
              placeholder="Enter your email or username"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="label">Password</label>
            <input
              id="password"
              className="input"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="button-primary" disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>

          {message && <p className="muted" style={{ color: '#059669' }}>{message}</p>}
          {error && <p className="muted" style={{ color: '#dc2626' }}>{error}</p>}
        </form>

        <p className="muted">
          Don\'t have an account?{' '}
          <button type="button" className="link" onClick={onToggleMode}>Sign up</button>
        </p>
      </div>
    </div>
  );
};

export default SignupForm; 