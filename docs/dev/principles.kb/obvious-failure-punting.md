# Obvious-failure punting (auto-YAGNI)

You may punt generalization, or special-case the present, **iff** the temporary
assumption fails loudly the moment it is violated. If it then never fails, the
generalization was unnecessary — auto-YAGNI proved itself.

Example: we ship one provider, `github`. Hardcoding it is fine because the day a
second platform appears, the github-keyed `get-context` errors out plainly
elsewhere — a red failure, not a silent wrong result.

This is the constructive pair of
[fail-closed](fail-closed-never-quietly-wrong.md): the shortcut is safe precisely
because the system *cannot be quietly wrong* about the assumption. A punt whose
violation would be silent is not allowed — that is just a latent bug.
