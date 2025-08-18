
import React from 'react';
import { TrashIcon } from './Icons';
import { useTranslation } from 'react-i18next';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ isOpen, onClose, onConfirm, title, message }) => {
  const { t } = useTranslation();
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-center items-center p-4" aria-modal="true" role="dialog">
      <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl w-full max-w-md animate-fade-in-up">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-500/20 sm:mx-0 sm:h-10 sm:w-10">
                <TrashIcon className="h-6 w-6 text-red-400" />
            </div>
            <div className="mt-0 text-left">
                <h3 className="text-lg font-semibold leading-6 text-on-surface-light dark:text-on-surface-dark" id="modal-title">{title}</h3>
                <div className="mt-2">
                    <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{message}</p>
                </div>
            </div>
          </div>
        </div>
        <div className="p-4 bg-secondary-light dark:bg-secondary-dark/50 rounded-b-xl flex justify-end gap-4">
          <button type="button" onClick={onClose} className="bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
            {t('common.cancel')}
          </button>
          <button type="button" onClick={onConfirm} className="bg-red-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-red-700 transition-colors">
            {t('confirmationModal.delete')}
          </button>
        </div>
      </div>
       <style>{`
        @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
            animation: fade-in-up 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default ConfirmationModal;