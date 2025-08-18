import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { useTheme } from './ThemeContext';

const Login: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    clientName: '',
    clientSlug: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, register } = useAuth();
  const { theme } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await login(formData.email, formData.password, formData.clientSlug || undefined);
      } else {
        await register(
          formData.email,
          formData.password,
          formData.clientName || undefined,
          formData.clientSlug || undefined
        );
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-on-surface-light dark:text-on-surface-dark">
            {isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}
          </h2>
          <p className="mt-2 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
            {isLogin ? 'Accede a tu backoffice' : 'Crea tu cuenta y empresa'}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg p-6 space-y-4">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-white/20 rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-2">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-white/20 rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Tu contraseña"
              />
            </div>

            {!isLogin && (
              <div>
                <label htmlFor="clientName" className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-2">
                  Nombre de tu Empresa
                </label>
                <input
                  id="clientName"
                  name="clientName"
                  type="text"
                  value={formData.clientName}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-white/20 rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Mi Empresa SpA"
                />
                <p className="mt-1 text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                  Deja vacio si ya tienes una empresa y conoces su codigo
                </p>
              </div>
            )}

            <div>
              <label htmlFor="clientSlug" className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-2">
                {isLogin ? 'Codigo de Empresa (opcional)' : 'Codigo de Empresa Existente (opcional)'}
              </label>
              <input
                id="clientSlug"
                name="clientSlug"
                type="text"
                value={formData.clientSlug}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-white/20 rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="mi-empresa"
              />
              <p className="mt-1 text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                {isLogin 
                  ? 'Si tienes multiples empresas, especifica cual usar'
                  : 'Si ya existe la empresa, usala en vez de crear una nueva'
                }
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Procesando...
                </div>
              ) : (
                isLogin ? 'Iniciar Sesion' : 'Crear Cuenta'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setFormData({ email: '', password: '', clientName: '', clientSlug: '' });
                }}
                className="text-sm text-primary hover:underline"
              >
                {isLogin 
                  ? 'No tienes cuenta? Crear una nueva'
                  : 'Ya tienes cuenta? Iniciar sesion'
                }
              </button>
            </div>
          </div>
        </form>

        <div className="mt-8 text-center">
          <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg p-4">
            <h3 className="text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-2">
              Sistema Multi-Tenant
            </h3>
            <div className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark space-y-1">
              <p>• Cada empresa tiene sus propios datos</p>
              <p>• Registro seguro con aislamiento total</p>
              <p>• Crea tu empresa o únete a una existente</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;