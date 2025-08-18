import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { GoogleGenAI } from '@google/genai';
import { mockProducts, mockOrders, mockClients } from '../constants';
import { SparklesIcon, XIcon, BotIcon, SendIcon } from './Icons';

type Message = {
  id: number;
  sender: 'user' | 'ai';
  text: string;
};

const TypingIndicator = () => (
    <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-on-surface-secondary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-on-surface-secondary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-on-surface-secondary rounded-full animate-bounce"></div>
    </div>
);

const IntelligentAssistant: React.FC = () => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const ai = useMemo(() => {
    // This is the only safe way to check for process.env in a browser-only environment.
    // Direct access (even in a try-catch) can cause a ReferenceError that crashes the app.
    if (typeof process !== 'undefined' && process.env && process.env.API_KEY) {
      try {
        return new GoogleGenAI({ apiKey: process.env.API_KEY });
      } catch (error) {
         console.error("Error initializing GoogleGenAI:", error);
         return null;
      }
    }
    console.warn("Intelligent Assistant is disabled: API_KEY not found or running in a browser-only environment.");
    return null;
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (query: string) => {
    if (!query.trim() || !ai) return;

    setMessages(prev => [...prev, { id: Date.now(), sender: 'user', text: query }]);
    setInput('');
    setIsLoading(true);

    const systemInstruction = `You are a helpful e-commerce dashboard assistant named 'Insight'. Your purpose is to answer questions based ONLY on the JSON data provided to you in the prompt. Do not make up information or answer questions outside of the provided data context. When asked about calculations (like totals, counts, averages), perform them accurately based on the data. When asked to list items, format them clearly. If the answer cannot be found in the provided data, respond with "I'm sorry, I don't have access to that information." or a similar polite refusal. Be concise and friendly in your responses. The data represents the current state of an e-commerce store.`;
    
    const contents = `
Here is the store data in JSON format:
\`\`\`json
{
  "products": ${JSON.stringify(mockProducts)},
  "orders": ${JSON.stringify(mockOrders)},
  "clients": ${JSON.stringify(mockClients)}
}
\`\`\`

Based on this data, please answer the following question: ${query}
`;

    try {
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: contents,
        config: {
          systemInstruction: systemInstruction,
        },
      });

      setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'ai', text: response.text }]);
    } catch (error) {
      console.error('Error calling Gemini API:', error);
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
      setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'ai', text: `Sorry, I encountered an error: ${errorMessage}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(input);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-8 right-8 bg-primary text-white w-16 h-16 rounded-full shadow-lg flex items-center justify-center z-50 hover:bg-primary/90 transition-transform transform hover:scale-110"
        aria-label={t('assistant.title')}
      >
        <SparklesIcon className="w-8 h-8" />
      </button>
      
      {isOpen && (
        <div className="fixed bottom-28 right-8 w-full max-w-md bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl z-50 flex flex-col animate-fade-in-up">
          <header className="p-4 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark">{t('assistant.title')}</h3>
            <button onClick={() => setIsOpen(false)} className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:text-on-surface-dark p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10">
              <XIcon className="w-6 h-6" />
            </button>
          </header>

          <div className="flex-1 p-4 space-y-4 overflow-y-auto h-96">
            {messages.length === 0 && !isLoading && (
              <div className="text-center p-4">
                 <div className="bg-primary/20 p-3 rounded-lg inline-block mb-4">
                    <BotIcon className="w-8 h-8 text-primary" />
                 </div>
                 <p className="text-on-surface-light dark:text-on-surface-dark font-semibold">{t('assistant.welcomeMessage')}</p>
                 <div className="mt-4 space-y-2 text-sm">
                    <button onClick={() => handleSendMessage(t('assistant.initialPrompt1'))} className="w-full text-left bg-secondary-light dark:bg-secondary-dark p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 transition-colors text-on-surface-secondary-light dark:text-on-surface-secondary-dark" disabled={!ai}>{t('assistant.initialPrompt1')}</button>
                    <button onClick={() => handleSendMessage(t('assistant.initialPrompt2'))} className="w-full text-left bg-secondary-light dark:bg-secondary-dark p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 transition-colors text-on-surface-secondary-light dark:text-on-surface-secondary-dark" disabled={!ai}>{t('assistant.initialPrompt2')}</button>
                    <button onClick={() => handleSendMessage(t('assistant.initialPrompt3'))} className="w-full text-left bg-secondary-light dark:bg-secondary-dark p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 transition-colors text-on-surface-secondary-light dark:text-on-surface-secondary-dark" disabled={!ai}>{t('assistant.initialPrompt3')}</button>
                 </div>
              </div>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`flex items-end gap-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.sender === 'ai' && (
                   <div className="flex-shrink-0 bg-secondary-light dark:bg-secondary-dark p-2 rounded-full">
                     <BotIcon className="w-5 h-5 text-on-surface-secondary-light dark:text-on-surface-secondary-dark" />
                   </div>
                )}
                <div className={`max-w-xs md:max-w-sm rounded-2xl px-4 py-2 ${msg.sender === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-secondary-light dark:bg-secondary-dark text-on-surface-light dark:text-on-surface-dark rounded-bl-none'}`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                </div>
              </div>
            ))}
             {isLoading && (
                <div className="flex items-end gap-2 justify-start">
                    <div className="flex-shrink-0 bg-secondary-light dark:bg-secondary-dark p-2 rounded-full">
                        <BotIcon className="w-5 h-5 text-on-surface-secondary-light dark:text-on-surface-secondary-dark" />
                    </div>
                    <div className="max-w-xs rounded-2xl px-4 py-2 bg-secondary-light dark:bg-secondary-dark text-on-surface-light dark:text-on-surface-dark rounded-bl-none">
                        <TypingIndicator />
                    </div>
                </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleFormSubmit} className="p-4 border-t border-gray-200 dark:border-white/10">
            <div className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={!ai ? "API Key not configured" : t('assistant.placeholder')}
                className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 pl-3 pr-10 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                disabled={isLoading || !ai}
              />
              <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-primary disabled:text-gray-600" disabled={isLoading || !input.trim() || !ai}>
                <SendIcon className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      )}
       <style>{`
        @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
            animation: fade-in-up 0.3s ease-out forwards;
        }
      `}</style>
    </>
  );
};

export default IntelligentAssistant;
