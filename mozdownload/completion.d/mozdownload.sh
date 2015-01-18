_mozdownload()
{
    local cur
    cur=${COMP_WORDS[COMP_CWORD]}

    COMPREPLY=()

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $( compgen -W '$(_MOZDOWNLOADARGCOMPLETE=1 mozdownload)' -- $cur ) )
    fi

    return 0

}
complete -f -F _mozdownload mozdownload
