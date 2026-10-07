import { Check, Loader2, Circle } from 'lucide-react';
import type { AgentStep } from '../types/clarion';

const STEPS: Omit<AgentStep, 'status'>[] = [
  { id: 1, name: 'Agent 1', description: 'Discourse Harvester' },
  { id: 2, name: 'Agent 2', description: 'Event Extractor' },
  { id: 3, name: 'Agent 3', description: 'Ontology Builder' },
  { id: 4, name: 'Agent 4', description: 'Synthesis & Forecasting' },
];

interface Props {
  currentStep: number; // 0=idle, 1-4=running that agent, 5=done
  error?: string | null;
}

export default function PipelineTracker({ currentStep, error }: Props) {
  if (currentStep === 0 && !error) return null;

  return (
    <div className="w-full max-w-3xl mx-auto fade-up">
      <div className="glass rounded-2xl p-5 border border-slate-700/50">
        <p className="text-xs text-slate-400 font-medium uppercase tracking-widest mb-4">
          Pipeline Status
        </p>
        <div className="flex items-center gap-0">
          {STEPS.map((step, i) => {
            const done = currentStep > step.id || currentStep === 5;
            const running = currentStep === step.id;
            const hasError = error && running;

            return (
              <div key={step.id} className="flex items-center flex-1">
                {/* Step circle */}
                <div className="flex flex-col items-center gap-1.5 flex-shrink-0">
                  <div className={`
                    w-9 h-9 rounded-full flex items-center justify-center border-2 transition-all duration-500
                    ${hasError
                      ? 'border-rose-500 bg-rose-900/30'
                      : done
                        ? 'border-emerald-500 bg-emerald-900/30'
                        : running
                          ? 'border-indigo-400 bg-indigo-900/30 step-running'
                          : 'border-slate-600 bg-slate-800/50'
                    }
                  `}>
                    {hasError ? (
                      <span className="text-rose-400 text-xs font-bold">!</span>
                    ) : done ? (
                      <Check size={16} className="text-emerald-400" />
                    ) : running ? (
                      <Loader2 size={16} className="text-indigo-400 animate-spin" />
                    ) : (
                      <Circle size={14} className="text-slate-600" />
                    )}
                  </div>
                  <div className="text-center">
                    <p className={`text-xs font-semibold ${running ? 'text-indigo-300' : done ? 'text-emerald-400' : 'text-slate-500'}`}>
                      {step.name}
                    </p>
                    <p className="text-[10px] text-slate-500 leading-tight max-w-16 text-center">
                      {step.description}
                    </p>
                  </div>
                </div>

                {/* Connector */}
                {i < STEPS.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-1 rounded transition-all duration-700 ${
                    currentStep > step.id + 1 || currentStep === 5 || (currentStep > step.id)
                      ? 'bg-emerald-500/60'
                      : 'bg-slate-700'
                  }`} />
                )}
              </div>
            );
          })}
        </div>

        {error && (
          <p className="mt-4 text-rose-400 text-xs bg-rose-900/20 border border-rose-800/50 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        {currentStep === 5 && !error && (
          <p className="mt-4 text-emerald-400 text-xs text-center animate-pulse">
            ✓ Intelligence Dossier Generated Successfully
          </p>
        )}
      </div>
    </div>
  );
}
