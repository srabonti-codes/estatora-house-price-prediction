import { useState } from 'react';
import { ArrowRight, House, LoaderCircle } from 'lucide-react';

const FEATURE_DEFAULTS = {
  'Neighborhood': 'NAmes',
  'Overall Qual': 7,
  'Overall Cond': 5,
  'Gr Liv Area': 1500,
  'Lot Area': 5000,
  'Year Built': 1970,
  'Year Remod/Add': 1995,
  'Total Bsmt SF': 900,
  'Garage Area': 400,
  'Garage Cars': 2,
  'Full Bath': 2,
  'Half Bath': 0,
  'Bedroom AbvGr': 3,
  'Kitchen Qual': 'TA',
  'Exter Qual': 'TA',
  'MS Zoning': 'RL',
  'Bldg Type': '1Fam',
  'House Style': '1Story',
  'Foundation': 'PConc',
  'Central Air': 'Y',
  'Sale Condition': 'Normal',
  'Sale Type': 'WD',
  Fireplaces: 0,
  'Mo Sold': 6,
  'Yr Sold': 2010,
};

const CATEGORY_FIELDS = [
  { title: 'Property basics', keys: ['MS Zoning', 'Neighborhood', 'Bldg Type', 'House Style', 'Lot Area', 'Gr Liv Area'] },
  { title: 'Quality & condition', keys: ['Overall Qual', 'Overall Cond', 'Kitchen Qual', 'Exter Qual', 'Foundation', 'Central Air'] },
  { title: 'Living space', keys: ['Total Bsmt SF', 'Garage Area', 'Garage Cars', 'Full Bath', 'Half Bath', 'Bedroom AbvGr', 'Fireplaces'] },
  { title: 'Timing & sale', keys: ['Year Built', 'Year Remod/Add', 'Mo Sold', 'Yr Sold', 'Sale Condition', 'Sale Type'] },
];

const NUMERIC_FIELDS = new Set([
  'Lot Area',
  'Gr Liv Area',
  'Overall Qual',
  'Overall Cond',
  'Total Bsmt SF',
  'Garage Area',
  'Garage Cars',
  'Full Bath',
  'Half Bath',
  'Bedroom AbvGr',
  'Fireplaces',
  'Year Built',
  'Year Remod/Add',
  'Mo Sold',
  'Yr Sold',
]);

const FIELD_OPTIONS = {
  'MS Zoning': ['A (agr)', 'C (all)', 'FV', 'I (all)', 'RH', 'RL', 'RM'],
  Neighborhood: ['Blmngtn', 'Blueste', 'BrDale', 'BrkSide', 'ClearCr', 'CollgCr', 'Crawfor', 'Edwards', 'Gilbert', 'Greens', 'GrnHill', 'IDOTRR', 'Landmrk', 'MeadowV', 'Mitchel', 'NAmes', 'NPkVill', 'NWAmes', 'NoRidge', 'NridgHt', 'OldTown', 'SWISU', 'Sawyer', 'SawyerW', 'Somerst', 'StoneBr', 'Timber', 'Veenker'],
  'Bldg Type': ['1Fam', '2fmCon', 'Duplex', 'Twnhs', 'TwnhsE'],
  'House Style': ['1.5Fin', '1.5Unf', '1Story', '2.5Fin', '2.5Unf', '2Story', 'SFoyer', 'SLvl'],
  'Kitchen Qual': ['Ex', 'Fa', 'Gd', 'Po', 'TA'],
  'Exter Qual': ['Ex', 'Fa', 'Gd', 'TA'],
  Foundation: ['BrkTil', 'CBlock', 'PConc', 'Slab', 'Stone', 'Wood'],
  'Central Air': ['N', 'Y'],
  'Sale Condition': ['Abnorml', 'AdjLand', 'Alloca', 'Family', 'Normal', 'Partial'],
  'Sale Type': ['COD', 'CWD', 'Con', 'ConLD', 'ConLI', 'ConLw', 'New', 'Oth', 'VWD', 'WD'],
};

const FIELD_HINTS = {
  'MS Zoning': 'Choose a zoning code from the Ames dataset.',
  Neighborhood: 'Choose a neighborhood code from the Ames dataset.',
  'Overall Qual': 'Overall material and finish quality (1–10).',
  'Overall Cond': 'Overall condition rating (1–9).',
  'Kitchen Qual': 'Kitchen quality: Po (poor) to Ex (excellent).',
  'Exter Qual': 'Exterior quality: Fa (fair) to Ex (excellent).',
  'Lot Area': 'Lot size in square feet.',
  'Gr Liv Area': 'Above-ground living area in square feet.',
  'Total Bsmt SF': 'Basement area in square feet.',
  'Garage Area': 'Garage area in square feet.',
  'Garage Cars': 'Garage capacity in cars.',
  'Full Bath': 'Number of full bathrooms.',
  'Half Bath': 'Number of half bathrooms.',
  'Bedroom AbvGr': 'Bedrooms above ground.',
  Fireplaces: 'Number of fireplaces.',
  'Year Built': 'Original construction year.',
  'Year Remod/Add': 'Year of the last remodel.',
  'Mo Sold': 'Sale month (1–12).',
  'Yr Sold': 'Sale year (Ames data: 2006–2010).',
  'Central Air': 'Central air conditioning: Y or N.',
};

const FIELD_LABELS = {
  'MS Zoning': 'Zoning',
  Neighborhood: 'Ames neighborhood',
  'Bldg Type': 'Building type',
  'House Style': 'House style',
  'Overall Qual': 'Overall quality',
  'Overall Cond': 'Overall condition',
  'Kitchen Qual': 'Kitchen quality',
  'Exter Qual': 'Exterior quality',
  Foundation: 'Foundation type',
  'Central Air': 'Central air',
  'Lot Area': 'Lot size',
  'Gr Liv Area': 'Above-ground living area',
  'Total Bsmt SF': 'Basement area',
  'Garage Area': 'Garage area',
  'Garage Cars': 'Garage capacity',
  'Full Bath': 'Full bathrooms',
  'Half Bath': 'Half bathrooms',
  'Bedroom AbvGr': 'Bedrooms above ground',
  Fireplaces: 'Fireplaces',
  'Year Built': 'Year built',
  'Year Remod/Add': 'Last remodel year',
  'Mo Sold': 'Sale month',
  'Yr Sold': 'Sale year',
  'Sale Condition': 'Sale condition',
  'Sale Type': 'Sale type',
};

const configuredApiUrl = import.meta.env.VITE_API_URL;
const apiBase = configuredApiUrl
  ? `${/^https?:\/\//i.test(configuredApiUrl) ? '' : 'https://'}${configuredApiUrl}`.replace(/\/+$/, '')
  : '';

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value || 0);

const parseValue = (value, fieldName) => {
  if (value === '') return null;
  if (NUMERIC_FIELDS.has(fieldName)) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return value;
};

function App() {
  const [formState, setFormState] = useState(FEATURE_DEFAULTS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleChange = (fieldName, value) => {
    setFormState((current) => ({ ...current, [fieldName]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const payload = Object.fromEntries(
        Object.entries(formState).map(([fieldName, value]) => [fieldName, parseValue(value, fieldName)]),
      );

      const response = await fetch(`${apiBase}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || 'Unable to estimate the house price.');
      }

      const data = await response.json();
      setResult(data);
    } catch (submitError) {
      setError(submitError.message || 'Something went wrong while predicting the price.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_#12352f,_#071411_42%,_#080d0c_100%)] text-stone-100">
      <header className="sticky top-0 z-10 border-b border-white/10 bg-[#080d0c]/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl items-center px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300 ring-1 ring-emerald-300/25">
              <House className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-semibold tracking-tight">Estatora</p>
              <p className="text-xs text-stone-400">Know the value. Make the move.</p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
          <form id="form" onSubmit={handleSubmit} className="overflow-hidden rounded-2xl border border-white/10 bg-[#101a16]/95 shadow-[0_24px_80px_-32px_rgba(0,0,0,0.8)] sm:rounded-3xl">
            <div className="border-b border-white/10 px-5 py-5 sm:px-8 sm:py-6">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                  <p className="text-xl font-semibold tracking-tight text-white sm:text-2xl">Property details</p>
                  <p className="mt-1 text-sm leading-6 text-stone-400">Enter a few home details to get a price estimate. Unlisted model details use typical values from the Ames dataset.</p>
              </div>
                <div className="w-fit rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-medium text-emerald-200">
                  Ames Housing model
                </div>
              </div>
            </div>

            <div className="space-y-7 px-5 py-6 sm:px-8 sm:py-8">
              {CATEGORY_FIELDS.map((group) => (
                <fieldset key={group.title} className="min-w-0 space-y-4">
                  <legend className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-200/80">{group.title}</legend>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {group.keys.map((fieldName) => (
                      <label key={fieldName} className="flex min-w-0 flex-col gap-2 text-sm font-medium text-stone-200">
                        <span>{FIELD_LABELS[fieldName] || fieldName}</span>
                        {FIELD_OPTIONS[fieldName] ? (
                          <select
                            value={formState[fieldName] ?? ''}
                            onChange={(event) => handleChange(fieldName, event.target.value)}
                            className="min-h-11 w-full min-w-0 rounded-xl border border-white/10 bg-[#0a110e] px-3.5 py-2.5 text-base text-white outline-none transition hover:border-white/20 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-300/10 sm:text-sm"
                            aria-label={fieldName}
                          >
                            <option value="">Select an option</option>
                            {FIELD_OPTIONS[fieldName].map((option) => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type={NUMERIC_FIELDS.has(fieldName) ? 'number' : 'text'}
                            value={formState[fieldName] ?? ''}
                            onChange={(event) => handleChange(fieldName, event.target.value)}
                            className="min-h-11 w-full min-w-0 rounded-xl border border-white/10 bg-[#0a110e] px-3.5 py-2.5 text-base text-white outline-none transition placeholder:text-stone-500 hover:border-white/20 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-300/10 sm:text-sm"
                            aria-label={fieldName}
                            inputMode={NUMERIC_FIELDS.has(fieldName) ? 'numeric' : undefined}
                            placeholder={NUMERIC_FIELDS.has(fieldName) ? 'Enter a value' : 'Type a value'}
                            min={fieldName === 'Overall Qual' || fieldName === 'Overall Cond' ? 1 : fieldName === 'Mo Sold' ? 1 : NUMERIC_FIELDS.has(fieldName) ? 0 : undefined}
                            max={fieldName === 'Overall Qual' ? 10 : fieldName === 'Overall Cond' ? 9 : fieldName === 'Mo Sold' ? 12 : undefined}
                            step="1"
                          />
                        )}
                        {FIELD_HINTS[fieldName] && (
                          <span className="text-xs font-normal leading-5 text-stone-500">{FIELD_HINTS[fieldName]}</span>
                        )}
                      </label>
                    ))}
                  </div>
                </fieldset>
              ))}

            <div className="flex flex-col gap-4 border-t border-white/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
              <button
                type="submit"
                disabled={isLoading}
                className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-emerald-300 px-5 py-3 text-sm font-semibold text-[#082017] transition hover:bg-emerald-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-200 disabled:cursor-not-allowed disabled:opacity-70 sm:w-auto"
              >
                {isLoading ? (
                  <>
                    <LoaderCircle className="h-4 w-4 animate-spin" />
                    Estimating...
                  </>
                ) : (
                  <>
                    Get price estimate
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>

              {result ? (
                <p aria-live="polite" className="text-lg font-semibold text-emerald-200 sm:text-right">{formatCurrency(result.predicted_price)}</p>
              ) : (
                <p className="text-sm text-stone-400 sm:text-right">Your estimate will appear here</p>
              )}
            </div>

            {error ? <p role="alert" className="rounded-xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</p> : null}
            </div>
          </form>
      </main>
    </div>
  );
}

export default App;
