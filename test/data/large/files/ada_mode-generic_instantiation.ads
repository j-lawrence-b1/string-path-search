-- Various generic_instantiations
-- test ada-parse-prj-file with no gpr file
--EMACSCMD:(and (eq ada-xref-tool 'gnat) (ada-parse-prj-file "ada_mode-no-gpr.adp"))
--EMACSCMD:(and (eq ada-xref-tool 'gnat) (ada-select-prj-file "ada_mode-no-gpr.adp"))

--EMACSCMD:(and (eq ada-xref-tool 'gnat) (progn (forward-line 2)(ada-find-other-file t)(looking-at "package Ada_Mode.Generic_Parent is")))
--EMACSRESULT:(eq ada-xref-tool 'gnat)
with Ada_Mode.Generic_Parent;
with Ada_Mode.Nominal;
private
package Ada_Mode.Generic_Instantiation is
   --EMACSCMD:(progn (end-of-line 0)(backward-word)(ada-next-statement-keyword)(looking-at "end Ada_Mode.Generic_Instantiation"))
   --EMACSRESULT:t

   --EMACSCMD:(jit-lock-fontify-now)

   --EMACSCMD:(test-face "Ada_Mode.Generic_Parent" 'font-lock-function-name-face)
   package Instance is new Ada_Mode.Generic_Parent;

   --EMACSCMD:(test-face "Instance.Generic_Function" 'font-lock-function-name-face)
   function Function_1 is new Instance.Generic_Function
     (Param_Type  => Integer,
      Result_Type => Boolean,
      Default     => False,
      Threshold   => 2);

   --EMACSCMD:(test-face "Instance.Generic_Procedure" 'font-lock-function-name-face)
   procedure Procedure_2 is new Instance.Generic_Procedure (Integer,
                                                            Function_1);

   --EMACSCMD:(test-face "Instance.Generic_Procedure" 'font-lock-function-name-face)
   procedure Procedure_3 is new Instance.Generic_Procedure
     (Integer, Function_1);

   -- multi-line font-lock doesn't work
   procedure Procedure_4 is new Instance.
     Generic_Procedure (Integer, Function_1);
   procedure Procedure_5 is new Instance
     .Generic_Procedure (Integer, Function_1);
   procedure Procedure_6 is new
     Instance.Generic_Procedure (Integer, Function_1);
   procedure Procedure_7 is
     new Instance.Generic_Procedure (Integer, Function_1);
   procedure Procedure_8
     is new Instance.Generic_Procedure (Integer, Function_1);

   -- multi-line works here, because this is in the parser
   --EMACSCMD:(progn (forward-line 2)(test-face "Instance.Generic_Function" 'font-lock-function-name-face))
   generic function Gen_Function_1 renames
     Instance.Generic_Function;

   --EMACSCMD:(progn (forward-line 2)(test-face "Instance.Generic_Function" 'font-lock-function-name-face))
   generic function Gen_Function_2
     renames Instance.Generic_Function;

   generic function
     Gen_Function_3 renames Instance.Generic_Function;
   generic
   function Gen_Function_4 renames Instance.Generic_Function;

   --EMACSCMD:(test-face "Instance.Generic_Procedure" 'font-lock-function-name-face)
   generic procedure Gen_Procedure_1 renames Instance.Generic_Procedure;
   generic procedure Gen_Procedure_2 renames
     Instance.Generic_Procedure;
   generic procedure Gen_Procedure_3
     renames Instance.Generic_Procedure;
   generic procedure
     Gen_Procedure_4 renames Instance.Generic_Procedure;
   generic
   procedure
     Gen_Procedure_5 renames Instance.Generic_Procedure;

   -- We are ignoring generic instantiations as overriding
   -- subprograms; there doesn't seem to be a way to declare one that
   -- is actually useful.

end Ada_Mode.Generic_Instantiation;
