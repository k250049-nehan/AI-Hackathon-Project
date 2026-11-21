# Mock CNIC Verification Guide (SIMULATED)

Sample operational guidance for the prototype. All identity records are mocked.

## Name spelling differences
Names such as Muhammad, Mohammad, Muhammed and Mohammed are treated as the same given name. Normalisation compares name tokens and never matches two people solely on a similar first name.

## Formatting
A CNIC contains 13 digits, usually written as XXXXX-XXXXXXX-X. Spaces and dashes are removed before checking. Malformed or missing CNIC numbers are reported as incomplete and never cause a crash or a wrong match.

## Weak connections
If the identity service cannot be reached, the case is saved locally on the device and synced later. A saved case is not approved until verification completes.

## Privacy
A citizen can withdraw consent at any time. After withdrawal, helpers and department staff can no longer read the citizen's record, and the withdrawal is written to the audit log.
